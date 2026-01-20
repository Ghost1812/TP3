/**
 * Schema GraphQL
 * Define tipos e queries disponiveis na API
 */
import { gql } from 'apollo-server-express';

export const typeDefs = gql`
  type Pais {
    nome: String!
    regiao: String!
    populacaoMilhoes: Float!
    populacaoTotal: Int!
    media30d: Float!
    maximo6m: Float!
  }

  type ContagemRegiao {
    regiao: String!
    total: Int!
  }

  type MediaPopulacao {
    regiao: String!
    mediaPopulacao: Float!
  }

  type Query {
    # Consulta 1: Agregar países (com filtro opcional por região)
    paises(regiao: String): [Pais!]!
    
    # Consulta 2: Contar países por região
    contagemPaisesPorRegiao: [ContagemRegiao!]!
    
    # Consulta 3: Média de população por região
    mediaPopulacaoPorRegiao: [MediaPopulacao!]!
    
    # Consulta XPath customizada
    consultarXPath(xpath: String!, idRequisicao: String): [String!]!
    
    # Aliases para compatibilidade (deprecated)
    ativos(tipo: String): [Pais!]! @deprecated(reason: "Use 'paises' instead")
    contagemAtivosPorTipo: [ContagemRegiao!]! @deprecated(reason: "Use 'contagemPaisesPorRegiao' instead")
    mediaPrecosPorTipo: [MediaPopulacao!]! @deprecated(reason: "Use 'mediaPopulacaoPorRegiao' instead")
  }
`;
