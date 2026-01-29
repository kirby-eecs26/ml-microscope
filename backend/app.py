@app.get("/captures")
def captures():
    try:
        data = client.list_captures()
        return {"captures": data}
    except Exception as e:
        raise