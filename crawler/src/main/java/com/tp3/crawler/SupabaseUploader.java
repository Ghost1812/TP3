package com.tp3.crawler;

import okhttp3.*;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class SupabaseUploader {
    private static final OkHttpClient client = new OkHttpClient();
    private static final Gson gson = new Gson();
    
    public static boolean uploadParaSupabase(String filename) {
        try {
            if (!Config.isSupabaseUrlValid()) {
                System.out.println("Erro upload: SUPABASE_URL inválida. Deve ser uma URL HTTP/HTTPS (ex: https://xxxxx.supabase.co)");
                return false;
            }
            
            gerenciarFIFO();
            
            File file = new File(filename);
            String url = Config.SUPABASE_URL + "/storage/v1/object/" + Config.SUPABASE_BUCKET + "/" + filename;
            
            Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", "Bearer " + Config.SUPABASE_KEY)
                .addHeader("Content-Type", "text/csv")
                .addHeader("x-upsert", "true")
                .post(RequestBody.create(Files.readAllBytes(file.toPath()), MediaType.parse("text/csv")))
                .build();
            
            try (Response response = client.newCall(request).execute()) {
                if (response.isSuccessful()) {
                    file.delete();
                    return true;
                } else {
                    System.out.println("Erro upload: HTTP " + response.code() + " - " + response.message());
                    if (response.body() != null) {
                        System.out.println("Resposta: " + response.body().string());
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("Erro upload: " + e.getMessage());
            if (e.getMessage() != null && e.getMessage().contains("postgresql")) {
                System.out.println("");
                System.out.println("ATENÇÃO: Parece que você está usando a string de conexão PostgreSQL!");
                System.out.println("SUPABASE_URL deve ser a URL da API REST (ex: https://xxxxx.supabase.co)");
                System.out.println("Encontre em: Supabase Dashboard > Settings > API > Project URL");
            }
        }
        return false;
    }
    
    private static void gerenciarFIFO() {
        try {
            List<String> csvs = listarCSVs();
            // Remover arquivos antigos até ter espaço para novo (manter máximo 2 antes de adicionar 1 = 3 total)
            while (csvs.size() >= Config.MAX_ARQUIVOS_BUCKET) {
                csvs.sort(String::compareTo);
                String arquivoAntigo = csvs.get(0);
                removerArquivo(arquivoAntigo);
                System.out.println("FIFO: Arquivo removido: " + arquivoAntigo);
                csvs.remove(0);
            }
        } catch (Exception e) {
            System.out.println("Erro FIFO: " + e.getMessage());
        }
    }
    
    private static List<String> listarCSVs() throws IOException {
        if (!Config.isSupabaseUrlValid()) {
            return new ArrayList<>();
        }
        
        String url = Config.SUPABASE_URL + "/storage/v1/object/list/" + Config.SUPABASE_BUCKET;
        Request request = new Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer " + Config.SUPABASE_KEY)
            .get()
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful()) {
                JsonArray files = gson.fromJson(response.body().string(), JsonArray.class);
                List<String> csvs = new ArrayList<>();
                for (int i = 0; i < files.size(); i++) {
                    String name = files.get(i).getAsJsonObject().get("name").getAsString();
                    if (name.endsWith(".csv")) csvs.add(name);
                }
                return csvs;
            }
        }
        return new ArrayList<>();
    }
    
    private static void removerArquivo(String filename) throws IOException {
        if (!Config.isSupabaseUrlValid()) {
            return;
        }
        
        String url = Config.SUPABASE_URL + "/storage/v1/object/" + Config.SUPABASE_BUCKET + "/" + filename;
        Request request = new Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer " + Config.SUPABASE_KEY)
            .delete()
            .build();
        
        client.newCall(request).execute().close();
    }
}
