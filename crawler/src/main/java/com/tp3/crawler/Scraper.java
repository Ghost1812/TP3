package com.tp3.crawler;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.By;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

/**
 * Classe responsável pela recolha de dados do site Worldometers.
 */
public class Scraper {

    /**
     * Extrai dados dos países e devolve uma lista de CountryData.
     */
    public static List<CountryData> extrairDadosPaises() {

        // Lista onde serão guardados os dados recolhidos
        List<CountryData> dados = new ArrayList<>();
        WebDriver driver = null;

        try {
            // Cria o navegador em modo headless
            driver = DriverBuilder.buildDriver(true);

            // Acede à página do Worldometers
            driver.get(Config.WORLDMETERS_URL);

            // Aguarda até que a tabela esteja disponível
            WebDriverWait wait = new WebDriverWait(
                driver, java.time.Duration.ofSeconds(20)
            );
            wait.until(
                ExpectedConditions.presenceOfElementLocated(By.tagName("table"))
            );

            // Pequena pausa para garantir carregamento completo
            Thread.sleep(2000);

            // Converte o HTML da página para um documento Jsoup
            Document doc = Jsoup.parse(driver.getPageSource());

            // Seleciona a primeira tabela encontrada
            Element tabela = doc.select("table").first();
            if (tabela == null) return dados;

            // Obtém todas as linhas da tabela
            Elements linhas = tabela.select("tr");
            int idx = 1;

            // Percorre as linhas da tabela (ignora o cabeçalho)
            for (Element linha : linhas) {
                if (idx++ == 1) continue;

                Elements cols = linha.select("td, th");
                if (cols.size() < 3) continue;

                try {
                    // Extrai o nome do país
                    String pais = cols.get(1).selectFirst("a") != null
                        ? cols.get(1).selectFirst("a").text().trim()
                        : cols.get(1).text().trim();

                    // Extrai e converte a população
                    String populacaoStr = cols.get(2)
                        .text().trim().replaceAll("[,\\s]", "");
                    long populacao = populacaoStr.isEmpty()
                        ? 0 : Long.parseLong(populacaoStr);

                    // Extrai a região, se existir
                    String regiao = cols.size() > 3
                        ? (cols.get(3).selectFirst("a") != null
                            ? cols.get(3).selectFirst("a").text().trim()
                            : cols.get(3).text().trim())
                        : "Desconhecido";

                    // Gera um identificador interno
                    String idInterno = "CSV_" +
                        pais.toUpperCase().replace(" ", "_")
                        .substring(0, Math.min(20, pais.length())) +
                        "_" + String.format("%03d", idx) + "_00";

                    // Cria e adiciona o objeto CountryData
                    dados.add(new CountryData(
                        idInterno,
                        pais,
                        regiao,
                        populacao / 1_000_000.0,
                        populacao,
                        LocalDateTime.now().format(
                            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
                        ),
                        "Pessoas"
                    ));

                } catch (Exception e) {
                    // Ignora erros de parsing numa linha específica
                }
            }

        } catch (Exception e) {
            System.out.println("Erro: " + e.getMessage());

        } finally {
            // Fecha o navegador
            if (driver != null) driver.quit();
        }

        // Devolve a lista de dados recolhidos
        return dados;
    }
}
