package com.tp3.crawler;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Crawler {
    private static final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    
    public static void main(String[] args) {
        if (Config.SUPABASE_URL.isEmpty() || Config.SUPABASE_KEY.isEmpty()) {
            System.out.println("Erro: Configure SUPABASE_URL e SUPABASE_KEY");
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
