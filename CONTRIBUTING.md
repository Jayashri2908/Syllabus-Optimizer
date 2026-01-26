# Contributing to SCDO

Thank you for your interest in contributing to the Syllabus and Curriculum Design Optimizer (SCDO)!

## How to Contribute

1.  **Fork the repository**
2.  **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3.  **Commit your changes** (`git commit -m 'Add some amazing feature'`)
4.  **Push to the branch** (`git push origin feature/amazing-feature`)
5.  **Open a Pull Request**

## Development Setup

1.  Clone the repository.
2.  Set up the python environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    pip install -r requirements.txt
    ```
3.  Set up the frontend:
    ```bash
    cd webapp/frontend
    npm install
    ```
4.  Configure `.env` using `.env.example` as a template.

## Code Style

-   **Python**: Follow PEP 8.
-   **JavaScript/React**: Follow standard React best practices.
