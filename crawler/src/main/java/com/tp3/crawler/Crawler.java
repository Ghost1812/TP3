package com.tp3.crawler;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Classe principal do Crawler.
 * Executa periodicamente a recolha de dados e o envio para o Supabase.
 */
public class Crawler {

    // Scheduler responsável por executar o crawler periodicamente
    private static final ScheduledExecutorService scheduler =
        Executors.newScheduledThreadPool(1);

    public static void main(String[] args) {

        // Verifica se as variáveis de ambiente do Supabase estão configuradas
        if (Config.SUPABASE_URL.isEmpty() || Config.SUPABASE_KEY.isEmpty()) {
            System.out.println("Erro: Configure SUPABASE_URL e SUPABASE_KEY");
            return;
        }

        // Valida se a URL do Supabase está no formato correto
        if (!Config.isSupabaseUrlValid()) {
            System.out.println("Erro: SUPABASE_URL inválida!");
            return;
        }

        // Inicia o crawler e executa o primeiro ciclo
        System.out.println("Crawler iniciado - Executando a cada 1 minuto");
        jobGerarEEnviar();

        // Agenda a execução periódica do crawler
        scheduler.scheduleAtFixedRate(
            Crawler::jobGerarEEnviar,
            1, 1, TimeUnit.MINUTES
        );

        // Garante encerramento correto do scheduler ao parar a aplicação
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Crawler parado");
            scheduler.shutdown();
        }));

        // Mantém a aplicação em execução
        try {
            Thread.sleep(Long.MAX_VALUE);
        } catch (InterruptedException e) {
            scheduler.shutdown();
        }
    }

    /**
     * Executa o processo de recolha, geração do CSV e upload.
     */
    private static void jobGerarEEnviar() {

        // Extrai os dados dos países
        List<CountryData> dados = Scraper.extrairDadosPaises();
        if (dados.isEmpty()) return;

        try {
            // Cria ficheiro CSV temporário
            String filename = CSVUtils.criarCSVTemporario(dados);

            // Envia o CSV para o Supabase Storage
            SupabaseUploader.uploadParaSupabase(filename);

        } catch (IOException e) {
            System.out.println("Erro: " + e.getMessage());
        }
    }
}
