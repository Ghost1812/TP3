package com.tp3.crawler;

import com.opencsv.CSVWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * Utilitários para criação de arquivos CSV
 */
public class CSVUtils {
    /**
     * Cria um arquivo CSV temporário com os dados dos países
     */
    public static String criarCSVTemporario(List<CountryData> dados) throws IOException {
        String filename = "pais_data_" + 
            LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")) + ".csv";
        
        try (CSVWriter writer = new CSVWriter(new FileWriter(filename))) {
            writer.writeNext(new String[]{"ID_Interno", "Ticker", "Tipo_Ativo", "Preco_Atual", 
                "Volume_Negociado", "Data_Negociacao", "Moeda"});
            
            for (CountryData d : dados) {
                writer.writeNext(new String[]{
                    d.getIdInterno(), d.getTicker(), d.getTipoAtivo(),
                    String.valueOf(d.getPrecoAtual()), String.valueOf(d.getVolumeNegociado()),
                    d.getDataNegociacao(), d.getMoeda()
                });
            }
        }
        return filename;
    }
}
