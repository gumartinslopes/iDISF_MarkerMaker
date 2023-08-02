# iDISF Marker Maker
Programa para a criação automática de marcadores para o iDISF utilizando erosão última(padrão) ou esqueletização. 
## Funcionamento
A geração de marcadores para o iDISF é feito em duas etapas. Primeiramente é gerada uma simplificação do objeto presente na imagem, seja por erosão última em que o objeto é reduzido até o pixel fundamental ou por esqueletização em que o objeto é reduzido para apenas o seu esqueleto. Após esse processo o programa irá realizar uma conversão do objeto simplificado para marcadores e salvar em um arquivo .txt;

## Parâmetros 
 - ``--input_dir``: Indica o diretório de entrada das imagens.
 - ``--output_dir``: Indica o diretório onde os marcadores serão armazenados.
 - ``--save_simplifications``:(T/Yes) Indica se as simplificações das imagens serão salvas. Por padrão, se não for indicado, este parâmetro é definido como não.
 - ``--simplification_dir``: Indica o diretório onde as simplificações serão armazenadas, se o parâmetro acima for selecionado.
 - ``--simplification_method``: (ue/skel)Indica o método de simplificação a ser utilizado. Por padrão o método de simplificação é definido para erosão última.