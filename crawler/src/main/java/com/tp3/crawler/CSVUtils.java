package com.tp3.crawler;

import com.opencsv.CSVWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * Classe utilitária para criação de ficheiros CSV.
 */
public class CSVUtils {

    /**
     * Cria um ficheiro CSV temporário com os dados dos países.
     */
    public static String criarCSVTemporario(List<CountryData> dados) throws IOException {

        // Gera o nome do ficheiro com data e hora
        String filename = "pais_data_" +
            LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")
            ) + ".csv";

        // Cria e escreve o ficheiro CSV
        try (CSVWriter writer = new CSVWriter(new FileWriter(filename))) {

            // Escreve o cabeçalho do CSV
            writer.writeNext(new String[]{
                "ID_Interno", "Nome_Pais", "Regiao",
                "Populacao_Milhoes", "Populacao_Total",
                "Data_Coleta", "Unidade"
            });

            // Escreve cada linha com os dados dos países
            for (CountryData d : dados) {
                writer.writeNext(new String[]{
                    d.getIdInterno(),
                    d.getNomePais(),
                    d.getRegiao(),
                    String.valueOf(d.getPopulacaoMilhoes()),
                    String.valueOf(d.getPopulacaoTotal()),
                    d.getDataColeta(),
                    d.getUnidade()
                });
            }
        }

        // Retorna o nome do ficheiro criado
        return filename;
    }
}
