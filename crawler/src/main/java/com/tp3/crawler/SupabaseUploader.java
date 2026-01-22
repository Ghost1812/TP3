package com.tp3.crawler;

import okhttp3.*;
import com.google.gson.Gson;
import com.google.gson.JsonArray;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;

/**
 * Classe responsável por enviar ficheiros CSV para o Supabase Storage.
 */
public class SupabaseUploader {

    // Cliente HTTP para comunicar com a API do Supabase
    private static final OkHttpClient client = new OkHttpClient();

    // Utilitário para tratar respostas em JSON
    private static final Gson gson = new Gson();

    /**
     * Faz o upload de um ficheiro CSV para o Supabase.
     * Aplica a política FIFO antes do envio.
     */
    public static boolean uploadParaSupabase(String filename) {
        try {
            // Valida a URL do Supabase
            if (!Config.isSupabaseUrlValid()) {
                System.out.println("Erro upload: SUPABASE_URL inválida");
                return false;
            }

            // Garante que o número máximo de ficheiros é respeitado
            gerenciarFIFO();

            File file = new File(filename);

            // URL do endpoint de upload
            String url = Config.SUPABASE_URL + "/storage/v1/object/"
                + Config.SUPABASE_BUCKET + "/" + filename;

            // Cria o pedido HTTP para enviar o CSV
            Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", "Bearer " + Config.SUPABASE_KEY)
                .addHeader("Content-Type", "text/csv")
                .addHeader("x-upsert", "true")
                .post(RequestBody.create(
                    Files.readAllBytes(file.toPath()),
                    MediaType.parse("text/csv")
                ))
                .build();

            // Executa o pedido
            try (Response response = client.newCall(request).execute()) {
                if (response.isSuccessful()) {
                    // Remove o ficheiro local após upload
                    file.delete();
                    return true;
                } else {
                    System.out.println("Erro upload: HTTP " + response.code());
                }
            }

        } catch (Exception e) {
            System.out.println("Erro upload: " + e.getMessage());

            // Aviso caso esteja a ser usada a string de conexão errada
            if (e.getMessage() != null && e.getMessage().contains("postgresql")) {
                System.out.println("SUPABASE_URL deve ser a URL da API REST");
            }
        }

        return false;
    }

    /**
     * Remove ficheiros antigos do bucket (FIFO).
     */
    private static void gerenciarFIFO() {
        try {
            List<String> csvs = listarCSVs();

            // Remove os ficheiros mais antigos até respeitar o limite
            while (csvs.size() >= Config.MAX_ARQUIVOS_BUCKET) {
                csvs.sort(String::compareTo);
                String arquivoAntigo = csvs.get(0);
                removerArquivo(arquivoAntigo);
                csvs.remove(0);
            }

        } catch (Exception e) {
            System.out.println("Erro FIFO: " + e.getMessage());
        }
    }

    /**
     * Lista os ficheiros CSV existentes no bucket.
     */
    private static List<String> listarCSVs() throws IOException {
        if (!Config.isSupabaseUrlValid()) {
            return new ArrayList<>();
        }

        // URL do endpoint de listagem
        String url = Config.SUPABASE_URL + "/storage/v1/object/list/"
            + Config.SUPABASE_BUCKET;

        Request request = new Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer " + Config.SUPABASE_KEY)
            .get()
            .build();

        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful()) {
                JsonArray files = gson.fromJson(
                    response.body().string(),
                    JsonArray.class
                );

                List<String> csvs = new ArrayList<>();

                // Filtra apenas ficheiros CSV
                for (int i = 0; i < files.size(); i++) {
                    String name = files.get(i)
                        .getAsJsonObject()
                        .get("name")
                        .getAsString();
                    if (name.endsWith(".csv")) csvs.add(name);
                }

                return csvs;
            }
        }

        return new ArrayList<>();
    }

    /**
     * Remove um ficheiro específico do bucket do Supabase.
     */
    private static void removerArquivo(String filename) throws IOException {
        if (!Config.isSupabaseUrlValid()) {
            return;
        }

        // URL do endpoint de remoção
        String url = Config.SUPABASE_URL + "/storage/v1/object/"
            + Config.SUPABASE_BUCKET + "/" + filename;

        Request request = new Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer " + Config.SUPABASE_KEY)
            .delete()
            .build();

        // Executa a remoção
        client.newCall(request).execute().close();
    }
}
