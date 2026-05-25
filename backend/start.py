import os
import sys

import uvicorn


def main() -> None:
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
