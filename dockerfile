FROM python:3.11.7

WORKDIR /app

COPY . .

RUN pip --no-cache-dir install -r requirements.txt 
    
EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
