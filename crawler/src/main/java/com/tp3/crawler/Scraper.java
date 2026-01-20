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
 * Classe responsável pelo scraping do site Worldometers
 */
public class Scraper {
    /**
     * Extrai dados de países do Worldometers usando Selenium
     */
    public static List<CountryData> extrairDadosPaises() {
        List<CountryData> dados = new ArrayList<>();
        WebDriver driver = null;
        
        try {
            driver = DriverBuilder.buildDriver(true);
            driver.get(Config.WORLDMETERS_URL);
            
            WebDriverWait wait = new WebDriverWait(driver, java.time.Duration.ofSeconds(20));
            wait.until(ExpectedConditions.presenceOfElementLocated(By.tagName("table")));
            Thread.sleep(2000);
            
            Document doc = Jsoup.parse(driver.getPageSource());
            Element tabela = doc.select("table").first();
            if (tabela == null) return dados;
            
            Elements linhas = tabela.select("tr");
            int idx = 1;
            
            // Processa cada linha da tabela (pula cabeçalho)
            for (Element linha : linhas) {
                if (idx++ == 1) continue;
                
                Elements cols = linha.select("td, th");
                if (cols.size() < 3) continue;
                
                try {
                    String pais = cols.get(1).selectFirst("a") != null 
                        ? cols.get(1).selectFirst("a").text().trim() 
                        : cols.get(1).text().trim();
                    
                    String populacaoStr = cols.get(2).text().trim().replaceAll("[,\\s]", "");
                    long populacao = populacaoStr.isEmpty() ? 0 : Long.parseLong(populacaoStr);
                    
                    String regiao = cols.size() > 3 
                        ? (cols.get(3).selectFirst("a") != null 
                            ? cols.get(3).selectFirst("a").text().trim() 
                            : cols.get(3).text().trim())
                        : "Desconhecido";
                    
                    String idInterno = "CSV_" + pais.toUpperCase().replace(" ", "_")
                        .substring(0, Math.min(20, pais.length())) + "_" + String.format("%03d", idx) + "_00";
                    String ticker = pais.length() > 10 
                        ? pais.substring(0, 10).toUpperCase().replace(" ", "_")
                        : pais.toUpperCase().replace(" ", "_");
                    
                    dados.add(new CountryData(
                        idInterno, ticker, regiao,
                        populacao / 1000000.0, populacao,
                        LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")),
                        "Pessoas"
                    ));
                } catch (Exception e) {
                    // Ignora linhas com erro de parsing
                }
            }
        } catch (Exception e) {
            System.out.println("Erro: " + e.getMessage());
        } finally {
            if (driver != null) driver.quit();
        }
        
        return dados;
    }
}
