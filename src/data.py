from typing import List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    SmallInteger,
    create_engine,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from datetime import datetime
from sqlalchemy.future import select

Base = declarative_base()


async def init_db(engine_url="sqlite+aiosqlite:///app.db"):
    engine = create_async_engine(engine_url, echo=False)  # Set echo to False
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


# Definición de las entidades
class Batch(Base):
    __tablename__ = "batch"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_inicial = Column(String(2048), nullable=False)
    fecha_creado = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_terminado = Column(DateTime, nullable=True)
    profundidad = Column(SmallInteger, nullable=True)
    sitios = Column(SmallInteger, nullable=True)
    caracteres = Column(SmallInteger, nullable=True)

    batch_sites = relationship("BatchSite", back_populates="batch")
    batch_prompts = relationship("BatchPrompt", back_populates="batch")
    new_prompts = []


class BatchSite(Base):
    __tablename__ = "batch_site"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batch.id"), nullable=False)
    url = Column(String(2048), nullable=False)
    contenido = Column(Text, nullable=True)
    fecha_creado = Column(DateTime, default=datetime.utcnow, nullable=False)

    batch = relationship("Batch", back_populates="batch_sites")
    responses = relationship("BatchPromptResponse", back_populates="batch_site")


class BatchPrompt(Base):
    __tablename__ = "batch_prompt"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batch.id"), nullable=False)
    prompt = Column(String(2048), nullable=False)

    batch = relationship("Batch", back_populates="batch_prompts")
    responses = relationship("BatchPromptResponse", back_populates="batch_prompt")


class BatchPromptResponse(Base):
    __tablename__ = "batch_prompt_response"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batch.id"), nullable=False)
    batch_site_id = Column(Integer, ForeignKey("batch_site.id"), nullable=False)
    batch_prompt_id = Column(Integer, ForeignKey("batch_prompt.id"), nullable=False)
    respuesta = Column(Text, nullable=False)
    fecha_creado = Column(DateTime, default=datetime.utcnow, nullable=False)

    batch_site = relationship("BatchSite", back_populates="responses")
    batch_prompt = relationship("BatchPrompt", back_populates="responses")


# Funciones para manejar cada entidad de manera asíncrona
async def create_batch(
    session, url_inicial, profundidad=None, sitios=None, caracteres=None
):
    batch = Batch(
        url_inicial=url_inicial,
        profundidad=profundidad,
        sitios=sitios,
        caracteres=caracteres,
        fecha_creado=datetime.now(),
        fecha_terminado=None,        
    )
    session.add(batch)
    await session.commit()
    await session.refresh(batch)
    return batch


async def create_batch_site(session, batch_id, url, contenido=None):
    batch_site = BatchSite(batch_id=batch_id, url=url, contenido=contenido)
    session.add(batch_site)
    await session.commit()
    await session.refresh(batch_site)
    return batch_site


async def create_batch_prompt(session, batch_id, prompt):
    batch_prompt = BatchPrompt(batch_id=batch_id, prompt=prompt)
    session.add(batch_prompt)
    await session.commit()
    await session.refresh(batch_prompt)
    return batch_prompt


async def create_batch_prompt_response(
    session, batch_id, batch_site_id, batch_prompt_id, respuesta
):
    response = BatchPromptResponse(
        batch_id=batch_id,
        batch_site_id=batch_site_id,
        batch_prompt_id=batch_prompt_id,
        respuesta=respuesta,
    )
    session.add(response)
    await session.commit()
    await session.refresh(response)
    return response


async def get_batches(session):
    result = await session.execute(select(Batch))
    return result.scalars().all()


async def get_batch(session, batch_id, eager: bool = False):
    if eager:
        result = await session.execute(
            select(Batch)
            .options(joinedload(Batch.batch_sites), joinedload(Batch.batch_prompts))
            .filter(Batch.id == batch_id)
        )
        return result.unique().scalars().one()
    else:
        return await session.get(Batch, batch_id)


async def get_batch_sites(session, batch_id):
    result = await session.execute(
        select(BatchSite).filter(BatchSite.batch_id == batch_id)
    )
    return result.scalars().all()


async def get_batch_site(session, batch_site_id):
    return await session.get(BatchSite, batch_site_id)


async def get_batch_prompts(session, batch_id):
    result = await session.execute(
        select(BatchPrompt).filter(BatchPrompt.batch_id == batch_id)
    )
    return result.scalars().all()


async def get_batch_prompt(session, batch_prompt_id):
    return await session.get(BatchPrompt, batch_prompt_id)


async def get_batch_responses(session, batch_id):
    result = await session.execute(
        select(BatchPromptResponse).filter(BatchPromptResponse.batch_id == batch_id)
    )
    return result.scalars().all()


async def update_batch(session, batch_id, **kwargs):
    try:
        batch = await session.get(Batch, batch_id)
        if not batch:
            print(f"Batch with id {batch_id} not found.")
            return None

        for key, value in kwargs.items():
            if hasattr(batch, key):
                print(f"Updating {key} to {value}")
                setattr(batch, key, value)
            else:
                print(f"Batch does not have attribute {key}")

        await session.commit()
        await session.refresh(batch)
        print(f"Batch {batch_id} updated successfully.")
        return batch
    except Exception as e:
        print(f"Error updating batch: {e}")
        await session.rollback()
        raise


async def update_batch_site(session, batch_site_id, **kwargs):
    batch_site = await session.get(BatchSite, batch_site_id)
    if not batch_site:
        return None

    for key, value in kwargs.items():
        if hasattr(batch_site, key):
            setattr(batch_site, key, value)

    await session.commit()
    await session.refresh(batch_site)
    return batch_site


# Ejemplo de inicialización
if __name__ == "__main__":
    import asyncio

    async def main():
        engine = await init_db()  # Await the coroutine to get the engine
        async_sessionmaker = sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_sessionmaker() as session:
            # Ejemplo de uso: Crear un batch
            new_batch = await create_batch(
                session,
                url_inicial="http://example.com",
                profundidad=2,
                sitios=10,
                caracteres=500,
            )
            print(f"Batch creado: {new_batch.id}")

    asyncio.run(main())
