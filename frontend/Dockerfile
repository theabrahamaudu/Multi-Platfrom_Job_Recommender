FROM python:3.10
WORKDIR /app
COPY requirements.txt .
COPY setup.py .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "Home.py"]
EXPOSE 8501