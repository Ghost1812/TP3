package com.tp3.crawler;

/**
 * Configurações do Crawler Service
 * Carrega variáveis de ambiente e valida configurações
 */
public class Config {
    public static final String SUPABASE_URL = System.getenv("SUPABASE_URL") != null 
        ? System.getenv("SUPABASE_URL").trim() : "";
    public static final String SUPABASE_KEY = System.getenv("SUPABASE_KEY") != null 
        ? System.getenv("SUPABASE_KEY").trim() : "";
    public static final String SUPABASE_BUCKET = System.getenv("SUPABASE_BUCKET") != null 
        ? System.getenv("SUPABASE_BUCKET").trim() : "tp3-data";
    
    public static final int MAX_ARQUIVOS_BUCKET = 3; // Máximo de arquivos CSV no bucket (FIFO)
    public static final String WORLDMETERS_URL = "https://www.worldometers.info/geography/countries-of-the-world/";
    
    /**
     * Valida se a URL do Supabase está correta
     * Deve ser uma URL HTTP/HTTPS, não a string de conexão PostgreSQL
     */
    public static boolean isSupabaseUrlValid() {
        if (SUPABASE_URL.isEmpty()) {
            return false;
        }
        String url = SUPABASE_URL.toLowerCase();
        return url.startsWith("http://") || url.startsWith("https://");
    }
}
