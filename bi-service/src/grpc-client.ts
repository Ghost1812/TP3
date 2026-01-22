/**
 * Cliente gRPC para comunicacao com XML Service
 * Implementa todas as operacoes de consulta disponiveis
 */
import * as grpc from '@grpc/grpc-js';
import protoLoader = require('@grpc/proto-loader');
import * as path from 'path';

const PROTO_PATH = path.join(__dirname, '../proto/xml_service.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const xmlServiceProto = grpc.loadPackageDefinition(packageDefinition) as any;

export interface Ativo {
  ticker: string;
  tipo: string;
  preco_atual: number;
  volume: number;
  media_30d: number;
  maximo_6m: number;
  capital?: string;
  subregiao?: string;
  moeda?: string;
  densidade?: number;
}

export interface ContagemTipo {
  tipo: string;
  total: number;
}

export interface MediaPreco {
  tipo: string;
  media_preco: number;
}

export class XMLServiceClient {
  private client: any;

  constructor(host: string, port: number) {
    const address = `${host}:${port}`;
    // Aumenta limite de tamanho da mensagem para 30MB (padrao e 4MB)
    const options = {
      'grpc.max_receive_message_length': 30 * 1024 * 1024, // 30MB
      'grpc.max_send_message_length': 30 * 1024 * 1024, // 30MB
    };
    this.client = new xmlServiceProto.xmlservice.XMLService(
      address,
      grpc.credentials.createInsecure(),
      options
    );
    console.log(`Conectado ao XML Service em ${address}`);
  }

  consultarXPath(xpath: string, idRequisicao?: string): Promise<{ sucesso: boolean; resultados: string[]; erro?: string }> {
    return new Promise((resolve, reject) => {
      this.client.ConsultarXPath(
        { xpath, id_requisicao: idRequisicao },
        (error: any, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve({
              sucesso: response.sucesso,
              resultados: response.resultados || [],
              erro: response.erro
            });
          }
        }
      );
    });
  }

  agregarAtivos(tipo?: string): Promise<{ sucesso: boolean; ativos: Ativo[]; erro?: string }> {
    return new Promise((resolve, reject) => {
      this.client.AgregarAtivos(
        { tipo },
        (error: any, response: any) => {
          if (error) {
            console.error('Erro gRPC ao agregar ativos:', error);
            resolve({
              sucesso: false,
              ativos: [],
              erro: error.message || 'Erro ao conectar com XML Service via gRPC'
            });
          } else {
            resolve({
              sucesso: response.sucesso,
              ativos: (response.ativos || []).map((a: any) => ({
                ticker: a.ticker,
                tipo: a.tipo,
                preco_atual: a.preco_atual,
                volume: a.volume,
                media_30d: a.media_30d,
                maximo_6m: a.maximo_6m,
                capital: a.capital || '',
                subregiao: a.subregiao || '',
                moeda: a.moeda || '',
                densidade: a.densidade || 0
              })),
              erro: response.erro
            });
          }
        }
      );
    });
  }

  contarAtivosPorTipo(): Promise<{ sucesso: boolean; contagens: ContagemTipo[]; erro?: string }> {
    return new Promise((resolve, reject) => {
      this.client.ContarAtivosPorTipo(
        {},
        (error: any, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve({
              sucesso: response.sucesso,
              contagens: (response.contagens || []).map((c: any) => ({
                tipo: c.tipo,
                total: c.total
              })),
              erro: response.erro
            });
          }
        }
      );
    });
  }

  mediaPrecosPorTipo(): Promise<{ sucesso: boolean; medias: MediaPreco[]; erro?: string }> {
    return new Promise((resolve, reject) => {
      this.client.MediaPrecosPorTipo(
        {},
        (error: any, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve({
              sucesso: response.sucesso,
              medias: (response.medias || []).map((m: any) => ({
                tipo: m.tipo,
                media_preco: m.media_preco
              })),
              erro: response.erro
            });
          }
        }
      );
    });
  }
}
