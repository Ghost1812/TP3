package com.tp3.crawler;

/**
 * Classe para representar dados de um país
 */
public class CountryData {
    private String idInterno;
    private String ticker;
    private String tipoAtivo;
    private double precoAtual;
    private long volumeNegociado;
    private String dataNegociacao;
    private String moeda;
    
    public CountryData(String idInterno, String ticker, String tipoAtivo, 
                      double precoAtual, long volumeNegociado, 
                      String dataNegociacao, String moeda) {
        this.idInterno = idInterno;
        this.ticker = ticker;
        this.tipoAtivo = tipoAtivo;
        this.precoAtual = precoAtual;
        this.volumeNegociado = volumeNegociado;
        this.dataNegociacao = dataNegociacao;
        this.moeda = moeda;
    }
    
    // Getters
    public String getIdInterno() { return idInterno; }
    public String getTicker() { return ticker; }
    public String getTipoAtivo() { return tipoAtivo; }
    public double getPrecoAtual() { return precoAtual; }
    public long getVolumeNegociado() { return volumeNegociado; }
    public String getDataNegociacao() { return dataNegociacao; }
    public String getMoeda() { return moeda; }
}
