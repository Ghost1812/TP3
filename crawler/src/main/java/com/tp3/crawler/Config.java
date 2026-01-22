package com.tp3.crawler;

/**
 * Classe de configuração do Crawler.
 * Contém constantes e variáveis de ambiente usadas no serviço.
 */
public class Config {

    // URL do Supabase Storage
    public static final String SUPABASE_URL = System.getenv("SUPABASE_URL") != null
        ? System.getenv("SUPABASE_URL").trim()
        : "";

    // Chave de autenticação do Supabase
    public static final String SUPABASE_KEY = System.getenv("SUPABASE_KEY") != null
        ? System.getenv("SUPABASE_KEY").trim()
        : "";

    // Nome do bucket onde os CSV são guardados
    public static final String SUPABASE_BUCKET = System.getenv("SUPABASE_BUCKET") != null
        ? System.getenv("SUPABASE_BUCKET").trim()
        : "tp3-data";

    // Número máximo de ficheiros CSV permitidos no bucket
    public static final int MAX_ARQUIVOS_BUCKET = 3;

    // URL do site usado para recolha dos dados
    public static final String WORLDMETERS_URL =
        "https://www.worldometers.info/geography/countries-of-the-world/";

    /**
     * Verifica se a URL do Supabase é válida.
     */
    public static boolean isSupabaseUrlValid() {
        if (SUPABASE_URL.isEmpty()) {
            return false;
        }

        String url = SUPABASE_URL.toLowerCase();
        return url.startsWith("http://") || url.startsWith("https://");
    }
}
