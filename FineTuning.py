from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported
from huggingface_hub import login
import torch
import os

# 鎵撳嵃鍙缁冨弬鏁扮殑鍑芥暟
def print_trainable_parameters(model):
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    ratio = (trainable_params / total_params) * 100
    print(f"鎬诲弬鏁伴噺: {total_params:,}")  
    print(f"鍙缁冨弬鏁伴噺: {trainable_params:,}") 
    print(f"璁粌鍙傛暟鍗犳瘮: {ratio:.4f}%") 

hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    login(hf_token)
else:
    print("HF_TOKEN not set; skipping huggingface login")

# 妫€鏌ュ彲鐢℅PU鏁伴噺
num_gpus = torch.cuda.device_count()
print(f"鍙敤GPU鏁伴噺: {num_gpus}")
for i in range(num_gpus):
    print(f"GPU {i}: {torch.cuda.get_device_name(i)}")

# 璁剧疆涓轰娇鐢ㄥ崟涓狦PU浠ラ伩鍏嶈澶囦笉鍖归厤闂
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # 鍙娇鐢ㄧ涓€涓狦PU

max_seq_length = 8196
dtype = None
load_in_4bit = True

# 浣跨敤鏈湴妯″瀷璺緞
model_path = "/root/model/Qwen2.5-VL-7B-Instruct"

# 鍔犺浇妯″瀷 - 浣跨敤鍗曚竴璁惧
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_path,
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
    device_map="cuda:0",  # 鏄庣‘鎸囧畾浣跨敤cuda:0璁惧
    local_files_only=True,
    use_auth_token=None,
    trust_remote_code=True
)

# 纭繚tokenizer鏈塸adding token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 瀹氫箟鏁版嵁鏍煎紡鍖栧嚱鏁?
def formatting_func(examples):
    formatted_texts = []
    
    for question, cot, response in zip(examples["Question"], examples["Complex_CoT"], examples["Response"]):
        formatted_text = f"""Below is an instruction that describes a task, paired with an input that provides further context.
Write a response that appropriately completes the request.
Before answering, think carefully about the question and create a step-by-step chain of thoughts to ensure a logical and accurate response.

### Instruction:
You are a medical expert with advanced knowledge in clinical reasoning, diagnostics, and treatment planning.
Please answer the following medical question.

### Question:
{question}

### Response:
<think>
{cot}
</think>
{response}{tokenizer.eos_token}"""
        
        formatted_texts.append(formatted_text)
    
    return {"text": formatted_texts}

# 鍔犺浇鏈湴JSON鏂囦欢
local_dataset_path = "filtered_medical_o1_sft_Chinese.json"
dataset = load_dataset("json", data_files=local_dataset_path, split="train")

# 搴旂敤鏍煎紡鍖栧嚱鏁?
dataset = dataset.map(
    formatting_func, 
    batched=True, 
    remove_columns=dataset.column_names
)

# 鍑嗗妯″瀷杩涜璁粌
FastLanguageModel.for_training(model)

# 搴旂敤LoRA寰皟鏂规硶
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
)

# 鎵撳嵃鍙缁冨弬鏁颁俊鎭?
print_trainable_parameters(model)

# 閰嶇疆璁粌鍙傛暟
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=20,
        num_train_epochs=1,
        learning_rate=1e-5,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=1,
        optim="adamw_torch",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
        report_to="none",
        hub_model_id=None,
        push_to_hub=False,
        # 浣跨敤鍗旼PU璁粌锛屼笉闇€瑕佸GPU鐩稿叧璁剧疆
    ),
)

# 寮€濮嬭缁?
try:
    trainer_stats = trainer.train()
    print("璁粌鎴愬姛瀹屾垚!")
except Exception as e:
    print(f"璁粌閬囧埌閿欒: {e}")
    import traceback
    traceback.print_exc()

# 寰皟鍚庡姞杞芥ā鍨嬭繘琛屾帹鐞?
try:
    FastLanguageModel.for_inference(model)
    
    # 瀹氫箟涓€涓祴璇曢棶棰?
    question = "涓€涓偅鏈夋€ユ€ч槕灏剧値鐨勭梾浜哄凡缁忓彂鐥?澶╋紝鑵圭棝绋嶆湁鍑忚交浣嗕粛鐒跺彂鐑紝鍦ㄤ綋妫€鏃跺彂鐜板彸涓嬭吂鏈夊帇鐥涚殑鍖呭潡锛屾鏃跺簲濡備綍澶勭悊锛?
    
    # 鏋勫缓杈撳叆
    prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context.
Write a response that appropriately completes the request.
Before answering, think carefully about the question and create a step-by-step chain of thoughts to ensure a logical and accurate response.

### Instruction:
You are a medical expert with advanced knowledge in clinical reasoning, diagnostics, and treatment planning.
Please answer the following medical question.

### Question:
{question}

### Response:
"""
    
    # 纭繚鎵€鏈夊紶閲忛兘鍦ㄥ悓涓€涓澶囦笂
    device = torch.device("cuda:0")  # 鏄庣‘鎸囧畾浣跨敤cuda:0璁惧
    inputs = tokenizer([prompt], return_tensors="pt").to(device)
    
    # 浣跨敤妯″瀷鐢熸垚鍥炵瓟
    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=1200,
        use_cache=True,
    )
    
    # 瑙ｇ爜妯″瀷鐢熸垚鐨勮緭鍑?
    response = tokenizer.batch_decode(outputs)
    print(response[0].split("### Response:")[1])
    
    # 淇濆瓨寰皟鍚庣殑妯″瀷鍜宼okenizer
    model.save_pretrained("lora_model")
    tokenizer.save_pretrained("lora_model")
    
except Exception as e:
    print(f"鎺ㄧ悊鎴栦繚瀛樿繃绋嬩腑閬囧埌閿欒: {e}")
    import traceback
    traceback.print_exc()
