/**
 * Crawler Service - TP3
 * Faz scraping do Worldometers e faz upload para Supabase Storage
 */
const puppeteer = require('puppeteer');
const { createClient } = require('@supabase/supabase-js');
const cron = require('node-cron');
const fs = require('fs');
const path = require('path');
const { createObjectCsvWriter } = require('csv-writer');

// Configuração Supabase
const SUPABASE_URL = process.env.SUPABASE_URL || '';
const SUPABASE_KEY = process.env.SUPABASE_KEY || '';
const SUPABASE_BUCKET = process.env.SUPABASE_BUCKET || 'market-data';

// URL do site para fazer crawl
const WORLDMETERS_URL = 'https://www.worldometers.info/geography/countries-of-the-world/';

/**
 * Extrai dados de países do Worldometers
 */
async function extrairDadosPaises() {
    const dados = [];
    let browser = null;
    
    try {
        console.log('Conectando ao Worldometers...');
        
        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--lang=en-US',
                '--window-size=1920,1080'
            ]
        });
        
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36');
        await page.setViewport({ width: 1920, height: 1080 });
        
        await page.goto(WORLDMETERS_URL, { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        // Aguardar tabela carregar
        await page.waitForSelector('table', { timeout: 20000 });
        
        // Aguardar renderização completa
        await page.waitForTimeout(2000);
        
        // Extrair dados da tabela
        const tabelaDados = await page.evaluate(() => {
            const tabelas = document.querySelectorAll('table');
            if (!tabelas || tabelas.length === 0) {
                return [];
            }
            
            const tabela = tabelas[0];
            const linhas = tabela.querySelectorAll('tr');
            const dados = [];
            
            for (let idx = 1; idx < linhas.length; idx++) {
                const linha = linhas[idx];
                const colunas = linha.querySelectorAll('td, th');
                
                if (colunas.length >= 3) {
                    try {
                        const rank = colunas[0].textContent.trim();
                        const paisLink = colunas[1].querySelector('a');
                        const pais = paisLink ? paisLink.textContent.trim() : colunas[1].textContent.trim();
                        const populacaoStr = colunas[2].textContent.trim();
                        const regiaoLink = colunas[3] ? colunas[3].querySelector('a') : null;
                        const regiao = regiaoLink ? regiaoLink.textContent.trim() : (colunas[3] ? colunas[3].textContent.trim() : '');
                        
                        // Limpar população (remover vírgulas e espaços)
                        const populacao = parseInt(populacaoStr.replace(/[,\s]/g, '')) || 0;
                        
                        dados.push({
                            rank,
                            pais,
                            populacao,
                            regiao: regiao || 'Desconhecido',
                            idx
                        });
                    } catch (e) {
                        console.error(`Erro ao processar linha ${idx}:`, e);
                    }
                }
            }
            
            return dados;
        });
        
        if (tabelaDados.length === 0) {
            console.log('Nenhuma tabela encontrada');
            return dados;
        }
        
        console.log(`Processando ${tabelaDados.length} linhas da tabela...`);
        
        // Processar e multiplicar dados por 10
        for (const item of tabelaDados) {
            const idInternoBase = `CSV_${item.pais.toUpperCase().replace(/ /g, '_').substring(0, 20)}_${String(item.idx).padStart(3, '0')}`;
            
            // Multiplicar dados por 10 (criar 10 registros para cada país)
            for (let multiplicador = 0; multiplicador < 10; multiplicador++) {
                dados.push({
                    'ID_Interno': `${idInternoBase}_${String(multiplicador).padStart(2, '0')}`,
                    'Ticker': item.pais.substring(0, 10).toUpperCase().replace(/ /g, '_'),
                    'Tipo_Ativo': item.regiao,
                    'Preco_Atual': item.populacao / 1000000.0,
                    'Volume_Negociado': item.populacao,
                    'Data_Negociacao': new Date().toISOString().replace('T', ' ').substring(0, 19),
                    'Moeda': 'Pessoas'
                });
            }
        }
        
        console.log(`Extraidos ${dados.length} registros (multiplicados por 10)`);
        
    } catch (error) {
        console.error('Erro ao fazer scraping:', error);
        console.error(error.stack);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
    
    return dados;
}

/**
 * Cria arquivo CSV temporário
 */
async function criarCsvTemporario(dados) {
    if (!dados || dados.length === 0) {
        throw new Error('Nenhum dado para criar CSV');
    }
    
    const timestamp = new Date().toISOString().replace(/[-:]/g, '').replace('T', '_').substring(0, 15);
    const filename = `market_data_${timestamp}.csv`;
    
    const csvWriter = createObjectCsvWriter({
        path: filename,
        header: Object.keys(dados[0]).map(key => ({ id: key, title: key }))
    });
    
    await csvWriter.writeRecords(dados);
    
    return filename;
}

/**
 * Gerencia FIFO: mantém máximo 3 CSVs no bucket, apaga o mais antigo
 */
async function gerenciarFifoBucket(supabase, novoArquivo) {
    try {
        // Listar todos os arquivos CSV no bucket
        const { data: arquivos, error: listError } = await supabase.storage
            .from(SUPABASE_BUCKET)
            .list();
        
        if (listError) {
            console.error('Erro ao listar arquivos:', listError);
            return;
        }
        
        // Filtrar apenas CSVs
        const csvs = arquivos.filter(f => f.name.endsWith('.csv'));
        
        // Se já tem 3 ou mais CSVs, ordenar por nome (timestamp) e apagar o mais antigo
        if (csvs.length >= 3) {
            // Ordenar por nome (que contém timestamp) - mais antigo primeiro
            const csvsOrdenados = csvs.sort((a, b) => a.name.localeCompare(b.name));
            
            // Apagar o mais antigo (primeiro da lista)
            const arquivoAntigo = csvsOrdenados[0].name;
            try {
                const { error: removeError } = await supabase.storage
                    .from(SUPABASE_BUCKET)
                    .remove([arquivoAntigo]);
                
                if (removeError) {
                    console.error(`Erro ao remover arquivo antigo: ${removeError}`);
                } else {
                    console.log(`Arquivo mais antigo removido (FIFO): ${arquivoAntigo}`);
                }
            } catch (e) {
                console.error(`Erro ao remover arquivo antigo: ${e}`);
            }
        }
    } catch (error) {
        console.error('Erro ao gerenciar FIFO:', error);
    }
}

/**
 * Faz upload do CSV para Supabase Storage com FIFO
 */
async function uploadParaSupabase(filename) {
    try {
        const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
        
        // Gerenciar FIFO antes de fazer upload
        await gerenciarFifoBucket(supabase, filename);
        
        // Ler arquivo
        const fileData = fs.readFileSync(filename);
        
        // Upload para o bucket
        const { data, error } = await supabase.storage
            .from(SUPABASE_BUCKET)
            .upload(filename, fileData, {
                contentType: 'text/csv',
                upsert: true
            });
        
        if (error) {
            throw error;
        }
        
        console.log(`CSV enviado para Supabase: ${filename}`);
        
        // Remove arquivo local após upload
        fs.unlinkSync(filename);
        
        return true;
    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        return false;
    }
}

/**
 * Job agendado para fazer scraping e enviar CSV
 */
async function jobGerarEEnviar() {
    const agora = new Date().toISOString().replace('T', ' ').substring(0, 19);
    console.log(`\n[${agora}] Iniciando scraping...`);
    
    const dados = await extrairDadosPaises();
    
    if (!dados || dados.length === 0) {
        console.log('Nenhum dado extraido');
        return;
    }
    
    console.log(`Extraidos ${dados.length} registros`);
    
    try {
        const filename = await criarCsvTemporario(dados);
        console.log(`CSV criado: ${filename}`);
        
        if (await uploadParaSupabase(filename)) {
            console.log('Processo concluido com sucesso');
        } else {
            console.log('Falha no processo');
        }
    } catch (error) {
        console.error('Erro ao processar CSV:', error);
    }
}

/**
 * Função principal
 */
function main() {
    console.log('='.repeat(60));
    console.log('CRAWLER SERVICE - TP3');
    console.log('='.repeat(60));
    console.log(`Supabase URL: ${SUPABASE_URL}`);
    console.log(`Bucket: ${SUPABASE_BUCKET}`);
    console.log('='.repeat(60));
    
    // Verificar configuração
    if (!SUPABASE_URL || !SUPABASE_KEY) {
        console.error('Erro: SUPABASE_URL e SUPABASE_KEY devem estar configurados');
        return;
    }
    
    // Executar imediatamente uma vez
    console.log('\n[INICIAL] Executando primeiro scraping...');
    jobGerarEEnviar().catch(console.error);
    
    // Agendar execução periódica (a cada 2 minutos)
    cron.schedule('*/2 * * * *', () => {
        jobGerarEEnviar().catch(console.error);
    });
    
    console.log('\nAgendado para executar a cada 2 minutos');
    console.log('Maximo de 3 CSVs no bucket (FIFO)');
    console.log('Pressione Ctrl+C para parar\n');
}

// Executar se for o arquivo principal
if (require.main === module) {
    main();
}

module.exports = { extrairDadosPaises, criarCsvTemporario, uploadParaSupabase };
