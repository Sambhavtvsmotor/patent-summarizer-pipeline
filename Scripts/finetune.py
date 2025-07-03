# finetune_bart.py

from datasets import load_dataset
from transformers import BartTokenizer, BartForConditionalGeneration, Trainer, TrainingArguments

# === Load dataset ===
dataset = load_dataset("json", data_files={
    "train": "./finetune_data/train.json",
    "test": "./finetune_data/test.json"
})

# === Tokenizer ===
model_name = "facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(model_name)

# === Tokenize ===
def preprocess(example):
    inputs = tokenizer(
        example["text"],
        max_length=1024,
        truncation=True
    )
    labels = tokenizer(
        example["summary"],
        max_length=150,
        truncation=True
    )
    inputs["labels"] = labels["input_ids"]
    return inputs

tokenized = dataset.map(preprocess, batched=True)

# === Model ===
model = BartForConditionalGeneration.from_pretrained(model_name)

# === TrainingArguments ===
training_args = TrainingArguments(
    output_dir="./domain-bart",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    learning_rate=5e-5,
    logging_steps=10,
    save_steps=50,
    evaluation_strategy="steps",
    eval_steps=50,
    fp16=False  # Set to True if you use GPU with mixed precision
)

# === Trainer ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"]
)

trainer.train()
trainer.save_model("./domain-bart")

print("✅ Domain-specific BART saved to ./domain-bart")
