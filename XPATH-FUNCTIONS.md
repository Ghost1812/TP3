# Funcionalidades XPath Disponíveis

O sistema utiliza PostgreSQL com a função `xpath()` que suporta **XPath 1.0**. Todas as consultas XPath são executadas sobre os documentos XML armazenados no banco de dados Supabase.

## Estrutura do XML

Os documentos XML seguem esta estrutura:

```xml
<RelatorioConformidade DataGeracao="2026-01-20" Versao="1.0">
  <Configuracao ValidadoPor="..." Requisitante="..."/>
  <Paises>
    <Pais IDInterno="CSV_INDIA_123" Nome="India">
      <DetalhesPais>
        <PopulacaoMilhoes>1428.63</PopulacaoMilhoes>
        <PopulacaoTotal>1428627663</PopulacaoTotal>
      </DetalhesPais>
      <DadosGeograficos>
        <Continente>Asia</Continente>
        <Subregiao>Southern Asia</Subregiao>
        <Capital>New Delhi</Capital>
        <Moeda>Indian rupee</Moeda>
        <DensidadePopulacao>431.21</DensidadePopulacao>
      </DadosGeograficos>
      <HistoricoAPI>
        <Media30d>0</Media30d>
        <Maximo6m>0</Maximo6m>
      </HistoricoAPI>
    </Pais>
    <!-- Mais países... -->
  </Paises>
</RelatorioConformidade>
```

## Funcionalidades XPath 1.0 Suportadas

### 1. Seletores Básicos

#### Selecionar elementos
- `/RelatorioConformidade/Paises/Pais` - Todos os elementos `Pais`
- `//Pais` - Todos os elementos `Pais` em qualquer nível (descendentes)
- `/RelatorioConformidade/Paises/Pais[1]` - Primeiro elemento `Pais`

#### Selecionar atributos
- `/RelatorioConformidade/Paises/Pais/@Nome` - Atributo `Nome` de todos os países
- `/RelatorioConformidade/Paises/Pais/@IDInterno` - Atributo `IDInterno`
- `//Pais/@Nome` - Atributo `Nome` usando busca descendente

#### Selecionar texto
- `/RelatorioConformidade/Paises/Pais/DadosGeograficos/Capital/text()` - Texto do elemento `Capital`
- `//Capital/text()` - Texto de todos os elementos `Capital`

### 2. Predicados (Filtros)

#### Filtros por atributo
- `/RelatorioConformidade/Paises/Pais[@Nome='India']` - País com nome "India"
- `/RelatorioConformidade/Paises/Pais[@IDInterno='CSV_INDIA_123']` - País com ID específico
- `//Pais[contains(@Nome, 'China')]` - Países cujo nome contém "China"

#### Filtros por conteúdo de elemento
- `/RelatorioConformidade/Paises/Pais[DadosGeograficos/Continente='Asia']` - Países da Ásia
- `//Pais[DadosGeograficos/Capital='Beijing']` - País com capital Beijing
- `//Pais[DetalhesPais/PopulacaoTotal > 1000000000]` - Países com população > 1 bilhão

#### Filtros combinados
- `/RelatorioConformidade/Paises/Pais[@Nome='India' and DadosGeograficos/Continente='Asia']`
- `//Pais[DadosGeograficos/Continente='Europe' or DadosGeograficos/Continente='Asia']`

### 3. Funções XPath 1.0

#### Funções de String
- `contains(@Nome, 'India')` - Verifica se o atributo contém a string
- `starts-with(@Nome, 'United')` - Verifica se começa com a string
- `substring(@Nome, 1, 5)` - Extrai substring
- `string-length(@Nome)` - Tamanho da string
- `normalize-space(text())` - Remove espaços extras

#### Funções Numéricas
- `number(DetalhesPais/PopulacaoTotal)` - Converte para número
- `sum(//PopulacaoTotal)` - Soma de valores
- `count(//Pais)` - Conta elementos
- `round(number(DetalhesPais/PopulacaoMilhoes))` - Arredonda número

#### Funções Booleanas
- `boolean(DetalhesPais/PopulacaoTotal)` - Converte para booleano
- `not(boolean(...))` - Negação

#### Funções de Posição
- `position()` - Posição do elemento atual
- `last()` - Última posição
- `/RelatorioConformidade/Paises/Pais[position() <= 10]` - Primeiros 10 países
- `/RelatorioConformidade/Paises/Pais[last()]` - Último país

### 4. Eixos XPath

- `child::Pais` - Filhos diretos (equivalente a `/Pais`)
- `descendant::Pais` - Descendentes (equivalente a `//Pais`)
- `parent::*` - Elemento pai
- `ancestor::RelatorioConformidade` - Ancestrais
- `following-sibling::Pais` - Irmãos seguintes
- `preceding-sibling::Pais` - Irmãos anteriores

### 5. Operadores

#### Operadores de Comparação
- `=` - Igualdade
- `!=` - Diferença
- `<` - Menor que
- `<=` - Menor ou igual
- `>` - Maior que
- `>=` - Maior ou igual

#### Operadores Lógicos
- `and` - E lógico
- `or` - OU lógico
- `not()` - Negação

#### Operadores Aritméticos
- `+` - Soma
- `-` - Subtração
- `*` - Multiplicação
- `div` - Divisão
- `mod` - Módulo

## Exemplos Práticos

### Consultas Simples

```xpath
# Todos os nomes de países
/RelatorioConformidade/Paises/Pais/@Nome

# Todas as capitais
//Capital/text()

# Todos os continentes únicos
//Continente/text()
```

### Consultas com Filtros

```xpath
# Países da Ásia
/RelatorioConformidade/Paises/Pais[DadosGeograficos/Continente='Asia']/@Nome

# Países com população > 1 bilhão
//Pais[number(DetalhesPais/PopulacaoTotal) > 1000000000]/@Nome

# Países da Europa com capital específica
//Pais[DadosGeograficos/Continente='Europe' and DadosGeograficos/Capital='Paris']/@Nome
```

### Consultas com Funções

```xpath
# Países cujo nome contém "United"
//Pais[contains(@Nome, 'United')]/@Nome

# Países ordenados por população (top 5)
//Pais[number(DetalhesPais/PopulacaoTotal) > 0][position() <= 5]/@Nome

# Soma total da população
sum(//PopulacaoTotal)

# Contagem de países por continente
count(//Pais[DadosGeograficos/Continente='Asia'])
```

### Consultas Avançadas

```xpath
# Países com densidade > 100 hab/km²
//Pais[number(DadosGeograficos/DensidadePopulacao) > 100]/@Nome

# Países da América (Norte ou Latina)
//Pais[DadosGeograficos/Continente='Northern America' or DadosGeograficos/Continente='Latin America']/@Nome

# Países cujo nome começa com "C"
//Pais[starts-with(@Nome, 'C')]/@Nome

# Países com moeda específica
//Pais[DadosGeograficos/Moeda='Euro']/@Nome
```

## Como Usar na Interface Web

1. Acesse a página de visualização
2. Na seção "Consultas XPath e XQuery"
3. Digite sua query XPath no campo de texto
4. (Opcional) Digite um ID de requisição para consultar apenas um documento específico
5. Clique em "Executar XPath"
6. Os resultados aparecerão na área de resultados abaixo

## Limitações

- O sistema suporta **XPath 1.0** (não XPath 2.0 ou 3.0)
- Algumas funções avançadas do XPath 2.0+ não estão disponíveis
- As consultas são executadas sobre todos os documentos XML no banco de dados (a menos que você especifique um `id_requisicao`)
- Resultados são retornados como array de strings

## Dicas

- Use `//` para busca em qualquer nível da árvore XML
- Use `text()` para obter o conteúdo textual de elementos
- Use `@` para acessar atributos
- Combine predicados com `and` e `or` para filtros complexos
- Use funções numéricas como `number()` para comparações numéricas
