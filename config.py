# config.py
class Config:
    # Default settings
    output_dir = r"C:\Users\iao\Desktop\PatStat_videre2\Patent_Familier_2024\patent_analyse\dataTable_NO_2020_2020"  # Placeholder default path
    country_code = "NO"
    start_year = 2020
    end_year = 2020
    batch_size = 200  # Example static setting
    ollama_base_url = "http://localhost:11434"  # Ollama base URL
    model_name = "llama3.2:latest"  # Model name for Ollama
    openai_model_name = "gpt-4o"  # Model name for OpenAI
    
    @classmethod
    def update(cls, **kwargs):
        """Update Config settings dynamically."""
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
            else:
                raise AttributeError(f"Unknown config attribute: {key}")
            
