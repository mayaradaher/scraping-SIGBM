# Raspagem de dados SIGBM

Este projeto tem como objetivo realizar a raspagem de dados das barragens localizadas no estado de Minas Gerais, disponíveis no site do [Sistema de Gestão de Segurança de Barragem de Mineração - SIGBM](https://app.anm.gov.br/SIGBM/Publico/GerenciarPublico) da Agência Nacional de Mineração (ANM).

#### Estrutura do Projeto

A raspagem é executada diariamente por meio de um *actions*. Os resultados são consolidados na pasta **data**, em que uma planilha no formato *.xlsx* é gerada, contendo os dados extraídos.

O projeto é estruturado em um pacote que engloba a pasta  **paginas_sigbm**, contendo o código de raspagem de cada página do site. Adicionalmente, inclui o arquivo  **setup.py**, que possibilita a execução do código.

#### Dicionário de dados

Para facilitar a compreensão dos dados raspados, há o dicionário de dados abaixo. A coluna **nome_sigbm** refere-se aos nomes dos campos conforme apresentados nas páginas do SIGBM, enquanto a coluna **nome_variavel** representa o campo *name* utilizado no código de inspeção dos elementos das páginas.


1. Disposição de Rejeitos com Barramento

| nome_sigbm                                                                                        | nome_variavel                                         |
| ------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Tipo de Barragem de Mineração                                                                   | TipoBarragemMineracao                                 |
| A Barragem de Mineração possui outra estrutura de mineração interna selante de reservatório? | BarragemInternaSelante                                |
| Quantidade Diques Internos                                                                        | QuantidadeDiqueInterno                                |
| Quantidade Diques Selantes                                                                        | QuantidadeDiqueSelante                                |
| A barragem de mineração possui ECJ?                                                             | BarragemPossuiBackUpDam                               |
| Esta ECJ está operando pós rompimento da barragem de mineração?                               | BackUpDamOperandoPosRompimento                        |
| Situação Operacional                                                                            | SituacaoOperacional                                   |
| Data de início da construção                                                                   | DataInicioConstrucao                                  |
| Data de início da construção - Indeterminada                                                   | SituacaoNivelEmergencialIndeterminadaInicioConstrucao |
| Data de início da operação                                                                     | DataInicioOperacao                                    |
| Data de início da descaracterização                                                            | DataInicioDescaracterizacao                           |
| Estrutura com o Objetivo de Contenção                                                           | EstruturaObjetivoContencao                            |
| A Barragem de Mineração está dentro da Área do Processo ANM ou da Área de Servidão          | BaragemDentroAreaProcesso                             |
| Barragem de mineração é alimentado por usina?                                                  | AlimentoUsina                                         |
| Usina                                                                                             | NomeUsina                                             |
| Não aparece no front-end do site                                                                 | DataDesativacao                                       |

1. 1 ECJ

| nome_sigbm                                                                                                      | nome_variavel                            |
| --------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Nome da ECJ                                                                                                     | NomeECJ                                  |
| Situação operacional da ECJ                                                                                   | SituacaoOperacional                      |
| Desde                                                                                                           | DataInicioSituacaoOperacional            |
| Vida útil prevista da Back Up Dam (Anos)                                                                       | VidaUtilPrevista_anos                    |
| A ECJ está dentro da Área do Processo ANM ou da Área de Servidão?                                           | DentroAreaProcesso                       |
| Processos associados                                                                                            | ProcessosAssociados                      |
| As coordenadas devem ser informadas em SIRGAS2000                                                               | CoordenadaSirga                          |
| Latitude                                                                                                        | Latitude                                 |
| Longitude                                                                                                       | Longitude                                |
| Altura Máxima do projeto da ECJ (m)                                                                            | AlturaMaximaProjeto_m                    |
| Comprimento da Crista do projeto da ECJ (m)                                                                     | ComprimentoCristaProjeto_m               |
| Volume do projeto da ECJ (m³)                                                                                  | VolumeProjetoReservatorio_m3             |
| Descarga Máxima do vertedouro da ECJ (m³/ seg)                                                                | DescargaMaximaVertedouro_m3_seg          |
| Existe documento que ateste a segurança estrutural e a capacidade para contenção de rejeitos da ECJ com ART? | ExisteDocumentoAtesteSeguranca           |
| Existe manual de operação da ECJ?                                                                             | ExisteManualOperacao                     |
| A ECJ passou por auditoria de terceira parte?                                                                   | PassouAuditoriaTerceiro                  |
| A ECJ garante a redução da área da mancha de inundação à jusante?                                         | GaranteReducaoAreaManchaInundacaoJusante |
| Tipo de ECJ quanto ao material de construção                                                                  | MateriaisConstrucao                      |
| Tipo de fundação da ECJ                                                                                       | TipoFundacao                             |
| Vazão de projeto da ECJ                                                                                        | VazaoProjeto                             |
| Método construtivo da ECJ                                                                                      | MetodoConstrutivo                        |
| Tipo de auscultação da ECJ                                                                                    | TipoAuscultacao                          |

1. 2 Descaracterização

| nome_sigbm                                               | nome_variavel                                |
| -------------------------------------------------------- | -------------------------------------------- |
| Fase Atual do projeto                                    | FaseAtualProjeto                             |
| Fase Atual do projeto detalhado                          | ElaboracaoProjeto                            |
| Data de emissão do projeto Básico                      | DataDeEmissaoProjetoBasico                   |
| Data estimada de emissão do projeto executivo           | DataEstimadaEmissaoProjeto                   |
| Data de emissão do projeto executivo                    | DataDeEmissaoProjetoExecutivo                |
| Qual foi a solução adotada para a descaracterização? | SolucaoDescaracterizacao                     |
| Descrição da Estrutura remanescente                    | EstruturaRemanescente                        |
| Fase de obras de estabilização ou descaracterização  | EstabilizacaoOuDescaracterizacao             |
| Data de início                                          | DataInicioEstabilizacaoOuDescaracterizacao   |
| Duração estimada em projeto (em meses)                 | DuracaoEstimadaEmMeses                       |
| Data de conclusão                                       | DataConlusaoEstabilizacaoOuDescaracterizacao |
| Em monitoramento ativo                                   | MonitoramentoAtivo                           |
| Data de início                                          | DataInicioMonitoramentoAtivo                 |
| Duração estimada em projeto (meses)                    | DuracaoMonitoramentoAtivoEmMeses             |
| Não aparece no front-end do site                        | DataEstimadaEmissaoProjeto                   |
| Não aparece no front-end do site                        | DataInicioMonitoramentoPassivo               |
| Não aparece no front-end do site                        | DataConclusaoMonitoramentoPassivo            |

2. Coordenadas do Centro da Crista

| nome_sigbm                                        | nome_variavel              |
| ------------------------------------------------- | -------------------------- |
| As coordenadas devem ser informadas em SIRGAS2000 | CoordenadasInformadasSirga |
| Latitude                                          | Latitude                   |
| Longitude                                         | Longitude                  |

3. Tipo de Rejeito Armazenado

| nome_sigbm                                                                       | nome_variavel                |
| -------------------------------------------------------------------------------- | ---------------------------- |
| Minério principal presente no reservatório                                     | MinerioPrincipalReservatorio |
| Processo de beneficiamento                                                       | ExisteProcessoBeneficiamento |
| Processo                                                                         | ProcessoBeneficiamento       |
| Produtos químicos utilizados                                                    | ProdutosQuimicosUtilizados   |
| A Barragem armazena rejeitos/residuos que contenham Cianeto?                     | BarragemArmazenaCianeto      |
| Teor (%) do minério principal inserido no rejeito                               | TeorMinerioInseridoRejeito_% |
| Outras substâncias minerais presentes no reservatório - Substância e Teor (%) | OutrasSubstanciasPresentes   |

4. Características Técnicas

| nome_sigbm                                               | nome_variavel                        |
| -------------------------------------------------------- | ------------------------------------ |
| Altura máxima do projeto licenciado (m)                 | AlturaMaximaProjetos_m               |
| Altura máxima atual (m)                                 | AlturaMaximaAtual_m                  |
| Comprimento da crista do projeto (m)                     | ComprimentoCristaProjeto_m           |
| Comprimento atual da crista (m)                          | ComprimentoAtualCrista_m             |
| Descarga máxima do vertedouro (m3 / seg)                | DescargaMaximaVertedouro_m3_seg      |
| Área do reservatório (m2)                              | AreaReservatorio_m2                  |
| Tipo de barragem quanto ao material de construção      | BarragemMaterialConstrucao           |
| Tipo de fundação                                       | TipoFundacao                         |
| Fundação                                               | Fundacao                             |
| Tempo de Recorrência da Vazão de projeto               | VazaoProjeto                         |
| Drenagem interna                                         | DrenagemInterna                      |
| Controle de compactação                                | ControleCompactacao                  |
| Inclinação média dos taludes na seção principal     | InclinacaoMediaTaludesSecaoPrincipal |
| Método construtivo da barragem                          | MetodoConstrutivoBarragem            |
| Tipo de alteamento                                       | TipoAlteamento                       |
| Instrumentação                                         | TipoAuscultacao                      |
| A barragem de mineração possui manta impermeabilizante | PossuiMantaImpermeabilizante         |

5. Estado de Conservação

| nome_sigbm                                | nome_variavel                        |
| ----------------------------------------- | ------------------------------------ |
| Confiabilidade das estruturas extravasora | ConfiabilidadeEstruturasEstravasoras |
| Percolação                              | Percolacao                           |
| Deformações e recalque                  | DeformacoesRecalques                 |
| Deteriorização dos taludes / paramentos | DeterioracaoTaludeParametro          |
| Drenagem superficial                      | DrenagemSuperficial                  |

6. Plano de Segurança

| nome_sigbm                                                                                                                                                           | nome_variavel                  |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| Documentação de projeto                                                                                                                                            | DocumentacaoProjeto            |
| Estrutura organizacional e qualificação técnica dos profissionais na equipe de Segurança da Barragem                                                            | EstruturaOrgTecSegBarragem     |
| Manuais de Procedimentos para Inspeções de Segurança e Monitoramento                                                                                              | ManuaisProcSegMonitoramento    |
| PAE - Plano de Ação Emergencial (quando exigido pelo órgão fiscalizador)                                                                                         | PlanoAcaoEmergencial           |
| As cópias físicas do PAEBM foram entregues para as Prefeituras e Defesas Civis municipais e estaduais, conforme exigido pelo art. 31 da Portaria nº 70.389/2017? | CopiaFisicaPAEBM               |
| Relatórios de inspeção e monitoramento da instrumentação e de Análise de Segurança                                                                            | RelMonitoramentoInspAnaliseSeg |

7. Dano Potencial Associado

| nome_sigbm                                                                            | nome_variavel                       |
| ------------------------------------------------------------------------------------- | ----------------------------------- |
| Volume de projeto licenciado do Reservatório (m³)                                   | VolumeProjetoReservatorio_m3        |
| Volume atual do Reservatório (m³)                                                   | VolumeAtualReservatorio_m3          |
| Capacidade Total do Reservatório (m³)                                               | CapacidadeTotalReservatorio         |
| Existência de população a jusante                                                  | ExistenciaPopulacaoJusante          |
| Número de pessoas possivelmente afetadas a jusante em caso de rompimento da barragem | NumeroPessoasAfetadasCasoRompimento |
| Impacto ambiental                                                                     | ImpactoAmbiental                    |
| Impacto sócio-econômico                                                             | ImpactoSocioEconomico               |
