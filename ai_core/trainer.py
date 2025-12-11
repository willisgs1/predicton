import os
import json
import torch
from peft import LoraConfig, get_peft_model, TaskType
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
from ai_core.llm import LocalMind

class SelfTrainer:
    def __init__(self, mind=None, training_file="workspace/training_data.jsonl", output_dir="ai_core/brain_adapters"):
        self.training_file = training_file
        self.output_dir = output_dir
        self.mind = mind if mind else LocalMind() # Loads the base model

    def train(self):
        """
        Fine-tunes the LocalMind using LoRA on the collected data.
        """
        if not os.path.exists(self.training_file):
            print("[Trainer] No training data found.")
            return

        print("[Trainer] Initiating Self-Improvement Protocol (LoRA)...")

        # 1. Prepare Model for LoRA
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,
            lora_alpha=32,
            lora_dropout=0.1
        )

        try:
            model = get_peft_model(self.mind.model, peft_config)
            model.print_trainable_parameters()

            # 2. Load Dataset (Simplified implementation)
            # In a full run, we would use 'datasets' library to load jsonl
            # Here we mock the dataset loading for the 'Seed' to avoid huge dependencies like 'datasets'
            # creating a dummy dataset class

            class SimpleDataset(torch.utils.data.Dataset):
                def __init__(self, file_path, tokenizer):
                    self.encodings = []
                    with open(file_path, 'r') as f:
                        for line in f:
                            data = json.loads(line)
                            # Convert chat format to text
                            text = f"<|im_start|>user\n{data['messages'][0]['content']}<|im_end|>\n<|im_start|>assistant\n{data['messages'][1]['content']}<|im_end|>"
                            self.encodings.append(tokenizer(text, truncation=True, padding="max_length", max_length=128))

                def __getitem__(self, idx):
                    item = {key: torch.tensor(val) for key, val in self.encodings[idx].items()}
                    item['labels'] = item['input_ids'].clone()
                    return item

                def __len__(self):
                    return len(self.encodings)

            train_dataset = SimpleDataset(self.training_file, self.mind.tokenizer)

            if len(train_dataset) < 10:
                print("[Trainer] Not enough data to train yet (Need 10+ samples).")
                return

            # 3. Training Args
            training_args = TrainingArguments(
                output_dir=self.output_dir,
                per_device_train_batch_size=1,
                num_train_epochs=1,
                learning_rate=2e-4,
                logging_steps=10,
                save_steps=100,
                use_cpu=not torch.cuda.is_available()
            )

            # 4. Train
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                data_collator=DataCollatorForLanguageModeling(self.mind.tokenizer, mlm=False),
            )

            trainer.train()

            # 5. Save Adapters
            model.save_pretrained(self.output_dir)
            print("[Trainer] Brain Surgery Complete. New instincts acquired.")

            # Clear data after training? Maybe keep for replay.
            # os.remove(self.training_file)

        except Exception as e:
            print(f"[Trainer] Training failed: {e}")

if __name__ == "__main__":
    # Create dummy data for test
    if not os.path.exists("workspace"): os.makedirs("workspace")
    with open("workspace/training_data.jsonl", "w") as f:
        for _ in range(15):
            f.write(json.dumps({"messages": [{"role": "user", "content": "test"}, {"role": "assistant", "content": "response"}]}) + "\n")

    trainer = SelfTrainer()
    trainer.train()
