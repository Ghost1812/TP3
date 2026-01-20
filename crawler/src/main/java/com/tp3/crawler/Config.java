package com.tp3.crawler;

/**
 * Configurações do Crawler Service
 */
public class Config {
    public static final String SUPABASE_URL = System.getenv("SUPABASE_URL") != null 
        ? System.getenv("SUPABASE_URL") : "";
    public static final String SUPABASE_KEY = System.getenv("SUPABASE_KEY") != null 
        ? System.getenv("SUPABASE_KEY") : "";
    public static final String SUPABASE_BUCKET = System.getenv("SUPABASE_BUCKET") != null 
        ? System.getenv("SUPABASE_BUCKET") : "tp3-data";
    
    public static final int MAX_ARQUIVOS_BUCKET = 3; // Máximo de arquivos CSV no bucket (FIFO)
    public static final String WORLDMETERS_URL = "https://www.worldometers.info/geography/countries-of-the-world/";
}
