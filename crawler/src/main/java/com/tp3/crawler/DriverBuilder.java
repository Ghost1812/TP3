package com.tp3.crawler;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

/**
 * Classe responsável pela criação e configuração do WebDriver.
 */
public class DriverBuilder {

    /**
     * Cria e devolve uma instância do WebDriver Chrome.
     */
    public static WebDriver buildDriver(boolean headless) {

        // Configura automaticamente o driver do Chrome
        WebDriverManager.chromedriver().setup();

        // Define opções de execução do navegador
        ChromeOptions options = new ChromeOptions();
        options.addArguments(
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage"
        );

        // Cria o WebDriver com as opções definidas
        WebDriver driver = new ChromeDriver(options);

        // Define o tempo máximo de carregamento das páginas
        driver.manage().timeouts().pageLoadTimeout(
            java.time.Duration.ofSeconds(30)
        );

        return driver;
    }
}
