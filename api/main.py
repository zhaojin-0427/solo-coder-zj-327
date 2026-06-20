from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import songs, members, formations, rehearsals, substitutes, statistics, performances, checklists, safety

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Community Dance Formation System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9511"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(songs.router)
app.include_router(members.router)
app.include_router(formations.router)
app.include_router(rehearsals.router)
app.include_router(substitutes.router)
app.include_router(statistics.router)
app.include_router(performances.router)
app.include_router(checklists.router)
app.include_router(safety.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9512, reload=True)
