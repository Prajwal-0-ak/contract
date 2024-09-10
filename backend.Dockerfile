FROM python:3.11-bullseye AS py_img

COPY ./backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /work_dir

COPY ./backend/ .

EXPOSE 8000

CMD ["python3", "api.py"]
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["fastapi", "run", "app/main.py", "--port", "80"]
