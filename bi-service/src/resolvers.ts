/**
 * Resolvers GraphQL
 * Implementa todas as queries disponiveis no schema
 */
import { XMLServiceClient } from './grpc-client';

export const resolvers = {
  Query: {
    paises: async (_: any, args: { regiao?: string }, context: { xmlServiceClient: XMLServiceClient }) => {
      const resultado = await context.xmlServiceClient.agregarAtivos(args.regiao);
      
      if (!resultado.sucesso) {
        throw new Error(resultado.erro || 'Erro ao buscar países');
      }
      
      return resultado.ativos.map(ativo => ({
        nome: ativo.ticker,
        regiao: ativo.tipo,
        populacaoMilhoes: ativo.preco_atual,
        populacaoTotal: ativo.volume,
        media30d: ativo.media_30d,
        maximo6m: ativo.maximo_6m
      }));
    },

    contagemPaisesPorRegiao: async (_: any, __: any, context: { xmlServiceClient: XMLServiceClient }) => {
      const resultado = await context.xmlServiceClient.contarAtivosPorTipo();
      
      if (!resultado.sucesso) {
        throw new Error(resultado.erro || 'Erro ao contar países');
      }
      
      return resultado.contagens.map(contagem => ({
        regiao: contagem.tipo,
        total: contagem.total
      }));
    },

    mediaPopulacaoPorRegiao: async (_: any, __: any, context: { xmlServiceClient: XMLServiceClient }) => {
      const resultado = await context.xmlServiceClient.mediaPrecosPorTipo();
      
      if (!resultado.sucesso) {
        throw new Error(resultado.erro || 'Erro ao calcular médias');
      }
      
      return resultado.medias.map(media => ({
        regiao: media.tipo,
        mediaPopulacao: media.media_preco
      }));
    },

    consultarXPath: async (_: any, args: { xpath: string; idRequisicao?: string }, context: { xmlServiceClient: XMLServiceClient }) => {
      const resultado = await context.xmlServiceClient.consultarXPath(args.xpath, args.idRequisicao);
      
      if (!resultado.sucesso) {
        throw new Error(resultado.erro || 'Erro ao executar XPath');
      }
      
      return resultado.resultados;
    },

    // Aliases para compatibilidade (deprecated - usar queries novas)
    ativos: async (_: any, args: { tipo?: string }, context: { xmlServiceClient: XMLServiceClient }) => {
      const resultado = await context.xmlServiceClient.agregarAtivos(args.tipo);
      
      if (!resultado.sucesso) {
        throw new Error(resultado.erro || 'Erro ao buscar países');
      }
      
      return resultado.ativos.map(ativo => ({
        nome: ativo.ticker,
        regiao: ativo.tipo,
        populacaoMilhoes: ativo.preco_atual,
        populacaoTotal: ativo.volume,
        media30d: ativo.media_30d,
        maximo6m: ativo.maximo_6m
      }));
    },

    contagemAtivosPorTipo: async (_: any, __: any, context: { xmlServiceClient: XMLServiceClient }) => {
      const resultado = await context.xmlServiceClient.contarAtivosPorTipo();
      
      if (!resultado.sucesso) {
        throw new Error(resultado.erro || 'Erro ao contar países');
      }
      
      return resultado.contagens.map(contagem => ({
        regiao: contagem.tipo,
        total: contagem.total
      }));
    },

    mediaPrecosPorTipo: async (_: any, __: any, context: { xmlServiceClient: XMLServiceClient }) => {
      const resultado = await context.xmlServiceClient.mediaPrecosPorTipo();
      
      if (!resultado.sucesso) {
        throw new Error(resultado.erro || 'Erro ao calcular médias');
      }
      
      return resultado.medias.map(media => ({
        regiao: media.tipo,
        mediaPopulacao: media.media_preco
      }));
    }
  }
};
