from src.core.provider.ollama_llm import OllamaProvider

llm = OllamaProvider(model_name='qwen2.5:14b-instruct-q4_K_M')

system_msg = "Bạn là trợ lý AI. Hãy trả lời câu hỏi của người dùng bằng tiếng Việt."
user_msg = f"Trong giới lập trình thi đấu, theo bạn thì ai là người giỏi nhất? Hãy cho tôi 1 cái tên"

print(llm.invoke(system_msg, user_msg))