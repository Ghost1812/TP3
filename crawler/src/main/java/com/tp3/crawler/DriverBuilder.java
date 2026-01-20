package com.tp3.crawler;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public class DriverBuilder {
    public static WebDriver buildDriver(boolean headless) {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage");
        WebDriver driver = new ChromeDriver(options);
        driver.manage().timeouts().pageLoadTimeout(java.time.Duration.ofSeconds(30));
        return driver;
    }
}
