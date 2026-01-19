/**
 * BI Service - TP3
 * Interface GraphQL/REST para consultas de dados
 */
import express from 'express';
import { ApolloServer } from 'apollo-server-express';
import cors from 'cors';
import { XMLServiceClient } from './grpc-client';
import { typeDefs } from './schema';
import { resolvers } from './resolvers';

const app = express();
app.use(cors());
app.use(express.json());

const XML_SERVICE_GRPC_HOST = process.env.XML_SERVICE_GRPC_HOST || 'xml-service';
const XML_SERVICE_GRPC_PORT = parseInt(process.env.XML_SERVICE_GRPC_PORT || '5000');
const PORT_REST = parseInt(process.env.PORT_REST || '3000');
const PORT_GRAPHQL = parseInt(process.env.PORT_GRAPHQL || '4000');

// Cliente gRPC
const xmlServiceClient = new XMLServiceClient(XML_SERVICE_GRPC_HOST, XML_SERVICE_GRPC_PORT);

// Endpoints REST
app.get('/health', (req, res) => {
  res.json({ status: 'OK', service: 'BI Service' });
});

// Consulta 1: Agregar ativos por tipo
app.get('/api/ativos', async (req, res) => {
  try {
    const tipo = req.query.tipo as string | undefined;
    const resultado = await xmlServiceClient.agregarAtivos(tipo);
    
    if (resultado.sucesso) {
      res.json({
        sucesso: true,
        dados: resultado.ativos,
        total: resultado.ativos.length
      });
    } else {
      res.status(500).json({
        sucesso: false,
        erro: resultado.erro
      });
    }
  } catch (error: any) {
    res.status(500).json({
      sucesso: false,
      erro: error.message
    });
  }
});

// Consulta 2: Contar ativos por tipo
app.get('/api/ativos/contagem-por-tipo', async (req, res) => {
  try {
    const resultado = await xmlServiceClient.contarAtivosPorTipo();
    
    if (resultado.sucesso) {
      res.json({
        sucesso: true,
        dados: resultado.contagens,
        total_tipos: resultado.contagens.length
      });
    } else {
      res.status(500).json({
        sucesso: false,
        erro: resultado.erro
      });
    }
  } catch (error: any) {
    res.status(500).json({
      sucesso: false,
      erro: error.message
    });
  }
});

// Consulta 3: Média de preços por tipo
app.get('/api/ativos/media-precos-por-tipo', async (req, res) => {
  try {
    const resultado = await xmlServiceClient.mediaPrecosPorTipo();
    
    if (resultado.sucesso) {
      res.json({
        sucesso: true,
        dados: resultado.medias
      });
    } else {
      res.status(500).json({
        sucesso: false,
        erro: resultado.erro
      });
    }
  } catch (error: any) {
    res.status(500).json({
      sucesso: false,
      erro: error.message
    });
  }
});

// Consulta XPath customizada
app.post('/api/xpath', async (req, res) => {
  try {
    const { xpath, id_requisicao } = req.body;
    
    if (!xpath) {
      return res.status(400).json({
        sucesso: false,
        erro: 'XPath é obrigatório'
      });
    }
    
    const resultado = await xmlServiceClient.consultarXPath(xpath, id_requisicao);
    
    if (resultado.sucesso) {
      res.json({
        sucesso: true,
        resultados: resultado.resultados,
        total: resultado.resultados.length
      });
    } else {
      res.status(500).json({
        sucesso: false,
        erro: resultado.erro
      });
    }
  } catch (error: any) {
    res.status(500).json({
      sucesso: false,
      erro: error.message
    });
  }
});

// Iniciar servidor GraphQL
async function startServer() {
  const apolloServer = new ApolloServer({
    typeDefs,
    resolvers,
    context: () => ({ xmlServiceClient })
  });

  await apolloServer.start();
  apolloServer.applyMiddleware({ app: app as any, path: '/graphql' });

  // Iniciar servidor Express
  app.listen(PORT_REST, () => {
    console.log('='.repeat(60));
    console.log('BI SERVICE - TP3');
    console.log('='.repeat(60));
    console.log(`REST API: http://localhost:${PORT_REST}`);
    console.log(`GraphQL: http://localhost:${PORT_REST}/graphql`);
    console.log(`XML Service gRPC: ${XML_SERVICE_GRPC_HOST}:${XML_SERVICE_GRPC_PORT}`);
    console.log('='.repeat(60));
  });
}

startServer().catch(console.error);
