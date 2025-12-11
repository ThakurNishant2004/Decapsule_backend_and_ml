from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.run import router as run_router
from routes.analyze import router as analyze_router
from routes.simulate import router as simulate_router
from routes.debug import router as debug_router
from routes.explain import router as explain_router
from routes.fix import router as fix_router
from routes.dp import router as dp_router
from routes.process import router as process_router
from routes.process_stream import router as process_stream_router



app = FastAPI(title="DECAPSULE Backend", description="AI Debugger Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_router, prefix="/run")
app.include_router(analyze_router, prefix="/analyze")
app.include_router(simulate_router, prefix="/simulate")
app.include_router(debug_router, prefix="/debug")
app.include_router(explain_router, prefix="/explain")
app.include_router(fix_router, prefix="/fix")
app.include_router(dp_router, prefix="/dp")
app.include_router(process_router, prefix="/process")
app.include_router(process_stream_router, prefix="/process_stream")


@app.get("/")
def root():
    return {"status": "ok", "service": "decapsule-backend"}
