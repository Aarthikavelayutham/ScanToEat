import google.generativeai as genai
genai.configure(api_key="AIzaSyDc-dLQ2vUb-3rq4i57ImKCmVyjnTPDPB8")
try:
    models = genai.list_models()
    for m in models:
        print(m.name, m.supported_generation_methods)
except Exception as e:
    print("Error:", e)
