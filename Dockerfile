FROM f66befd33669
ADD test.py /
ADD pks /usr/bin
ADD kubectl /usr/bin
CMD ["python", "./test.py"]
