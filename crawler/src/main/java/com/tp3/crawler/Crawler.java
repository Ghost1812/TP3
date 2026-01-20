package com.tp3.crawler;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Classe principal do Crawler
 * Executa scraping do Worldometers a cada 1 minuto e faz upload para Supabase
 */
public class Crawler {
    private static final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    
    public static void main(String[] args) {
        if (Config.SUPABASE_URL.isEmpty() || Config.SUPABASE_KEY.isEmpty()) {
            System.out.println("Erro: Configure SUPABASE_URL e SUPABASE_KEY");
            System.out.println("");
            System.out.println("SUPABASE_URL deve ser a URL da API REST do Supabase (ex: https://xxxxx.supabase.co)");
            System.out.println("NÃO use a string de conexão PostgreSQL!");
            System.out.println("");
            System.out.println("Configure as variáveis de ambiente:");
            System.out.println("  $env:SUPABASE_URL = \"https://seu-projeto.supabase.co\"");
            System.out.println("  $env:SUPABASE_KEY = \"sua-chave-anon-key\"");
            return;
        }
        
        if (!Config.isSupabaseUrlValid()) {
            System.out.println("Erro: SUPABASE_URL inválida!");
            System.out.println("");
            System.out.println("A URL deve começar com 'http://' ou 'https://'");
            System.out.println("Valor atual: " + Config.SUPABASE_URL);
            System.out.println("");
            System.out.println("SUPABASE_URL deve ser a URL da API REST do Supabase:");
            System.out.println("  Exemplo correto: https://xxxxx.supabase.co");
            System.out.println("  Exemplo ERRADO: postgresql://... (essa é a string de conexão do banco)");
            System.out.println("");
            System.out.println("Encontre a URL correta em: Supabase Dashboard > Settings > API > Project URL");
            return;
        }
        
        System.out.println("Crawler iniciado - Executando a cada 1 minuto");
        jobGerarEEnviar();
        
        scheduler.scheduleAtFixedRate(Crawler::jobGerarEEnviar, 1, 1, TimeUnit.MINUTES);
        
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Crawler parado");
            scheduler.shutdown();
        }));
        
        try {
            Thread.sleep(Long.MAX_VALUE);
        } catch (InterruptedException e) {
            scheduler.shutdown();
        }
    }
    
    /**
     * Job principal: extrai dados, cria CSV e faz upload
     */
    private static void jobGerarEEnviar() {
        List<CountryData> dados = Scraper.extrairDadosPaises();
        if (dados.isEmpty()) return;
        
        try {
            String filename = CSVUtils.criarCSVTemporario(dados);
            SupabaseUploader.uploadParaSupabase(filename);
        } catch (IOException e) {
            System.out.println("Erro: " + e.getMessage());
        }
    }
}
