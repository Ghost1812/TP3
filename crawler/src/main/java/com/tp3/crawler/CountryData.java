package com.tp3.crawler;

/**
 * Classe que representa os dados de um país recolhidos pelo crawler.
 */
public class CountryData {

    // Identificador interno do registo
    private String idInterno;

    // Nome do país
    private String nomePais;

    // Região ou continente do país
    private String regiao;

    // População do país em milhões
    private double populacaoMilhoes;

    // População total do país
    private long populacaoTotal;

    // Data em que os dados foram recolhidos
    private String dataColeta;

    // Unidade utilizada para os valores apresentados
    private String unidade;

    /**
     * Construtor da classe CountryData.
     */
    public CountryData(String idInterno, String nomePais, String regiao,
                       double populacaoMilhoes, long populacaoTotal,
                       String dataColeta, String unidade) {

        this.idInterno = idInterno;
        this.nomePais = nomePais;
        this.regiao = regiao;
        this.populacaoMilhoes = populacaoMilhoes;
        this.populacaoTotal = populacaoTotal;
        this.dataColeta = dataColeta;
        this.unidade = unidade;
    }

    // Métodos getters para acesso aos dados
    public String getIdInterno() { return idInterno; }
    public String getNomePais() { return nomePais; }
    public String getRegiao() { return regiao; }
    public double getPopulacaoMilhoes() { return populacaoMilhoes; }
    public long getPopulacaoTotal() { return populacaoTotal; }
    public String getDataColeta() { return dataColeta; }
    public String getUnidade() { return unidade; }
}
