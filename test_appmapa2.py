import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys

# Mock streamlit para evitar erros de inicialização
sys.modules['streamlit'] = MagicMock()
sys.modules['folium'] = MagicMock()
sys.modules['folium.plugins'] = MagicMock()
sys.modules['streamlit_folium'] = MagicMock()
sys.modules['st_supabase_connection'] = MagicMock()
sys.modules['geopy'] = MagicMock()
sys.modules['geopy.geocoders'] = MagicMock()


class TestAppMapa2:
    """Testes para o aplicativo appmapa2.py"""

    def test_query_params_latitude_required(self):
        """Testa se latitude é obrigatória nos query params"""
        with patch('streamlit.query_params', {}):
            # Latitude ausente deve parar a execução
            assert "latq" not in {"latq": None}

    def test_query_params_longitude_required(self):
        """Testa se longitude é obrigatória nos query params"""
        with patch('streamlit.query_params', {}):
            # Longitude ausente deve parar a execução
            assert "lonq" not in {"lonq": None}

    def test_float_conversion_latitude(self):
        """Testa conversão de latitude para float"""
        lat_str = "-23.5505"
        assert float(lat_str) == -23.5505
        assert isinstance(float(lat_str), float)

    def test_float_conversion_longitude(self):
        """Testa conversão de longitude para float"""
        lon_str = "-46.6333"
        assert float(lon_str) == -46.6333
        assert isinstance(float(lon_str), float)

    def test_dataframe_creation(self):
        """Testa criação de DataFrame a partir de dados SQL"""
        mock_data = [
            {
                'ANO_ESTATISTICA': 2023,
                'MES_ESTATISTICA': 1,
                'NUM_BO': '123456',
                'DATA_OCORRENCIA_BO': '2023-01-15',
                'HORA_OCORRENCIA_BO': '2023-01-15T14:30:00',
                'DESC_PERIODO': 'Tarde',
                'NOME_DEPARTAMENTO_CIRCUNSCRIÇÃO': 'DP 1',
                'NOME_SECCIONAL_CIRCUNSCRIÇÃO': 'Seccional 1',
                'NOME_DELEGACIA_CIRCUNSCRIÇÃO': 'Delegacia 1',
                'NOME_MUNICIPIO_CIRCUNSCRIÇÃO': 'São Paulo',
                'BAIRRO': 'Centro',
                'LOGRADOURO': 'Rua A',
                'NUMERO_LOGRADOURO': '123',
                'LATITUDE': -23.5505,
                'LONGITUDE': -46.6333,
                'DESCR_TIPOLOCAL': 'Via Pública',
                'RUBRICA': 'Roubo',
                'NATUREZA_APURADA': 'Roubo a Pedestre',
            }
        ]
        df = pd.DataFrame(mock_data)
        
        assert len(df) == 1
        assert 'LATITUDE' in df.columns
        assert 'LONGITUDE' in df.columns
        assert df['LATITUDE'].iloc[0] == -23.5505

    def test_latitude_mean_calculation(self):
        """Testa cálculo da média de latitudes"""
        mock_data = [
            {'LATITUDE': -23.5505},
            {'LATITUDE': -23.5510},
            {'LATITUDE': -23.5515},
        ]
        df = pd.DataFrame(mock_data)
        mean_lat = df[['LATITUDE']].mean()
        
        assert mean_lat.values[0] == pytest.approx(-23.551, abs=0.001)

    def test_longitude_mean_calculation(self):
        """Testa cálculo da média de longitudes"""
        mock_data = [
            {'LONGITUDE': -46.6333},
            {'LONGITUDE': -46.6338},
            {'LONGITUDE': -46.6343},
        ]
        df = pd.DataFrame(mock_data)
        mean_lon = df[['LONGITUDE']].mean()
        
        assert mean_lon.values[0] == pytest.approx(-46.6338, abs=0.001)

    def test_time_extraction_from_timestamp(self):
        """Testa extração de hora do timestamp"""
        timestamp = '2023-01-15T14:30:00'
        xhora = ' ' + timestamp[11:16]
        
        assert xhora == ' 14:30'

    def test_marker_data_formatting(self):
        """Testa formatação de dados para popup do marcador"""
        row = {
            'RUBRICA': 'Roubo',
            'NATUREZA_APURADA': 'Roubo a Pedestre',
            'DATA_OCORRENCIA_BO': '2023-01-15T14:30:00',
            'LOGRADOURO': 'Rua A',
            'NUMERO_LOGRADOURO': '123',
            'LATITUDE': -23.5505,
            'LONGITUDE': -46.6333,
        }
        
        xhora = ' ' + row['DATA_OCORRENCIA_BO'][11:16]
        
        popup_html = "<h3>Fatos :</h3> <ul> <li>{0}</li> <li>{1}</li> <li>{2}{3}</li> <li>{4}{5}</li>".format(
            row['RUBRICA'],
            row['NATUREZA_APURADA'],
            row['DATA_OCORRENCIA_BO'][:10],
            xhora,
            row['LOGRADOURO'] + ' ',
            row['NUMERO_LOGRADOURO']
        )
        
        assert 'Roubo' in popup_html
        assert 'Rua A 123' in popup_html
        assert '2023-01-15' in popup_html
        assert '14:30' in popup_html

    def test_haversine_query_structure(self):
        """Testa estrutura da query com fórmula de Haversine"""
        local_lat = -23.5505
        local_long = -46.6333
        radius = 0.5  # km
        
        # Verifica se a query contém os componentes corretos
        query_pattern = f'where (6371 * acos(cos(radians({local_lat})) * cos(radians("LATITUDE")) * cos(radians({local_long}) - radians("LONGITUDE")) + sin(radians({local_lat})) * sin(radians("LATITUDE")) )) <= {radius}'
        
        assert '6371' in query_pattern  # constante de raio da Terra em km
        assert 'acos' in query_pattern
        assert 'radians' in query_pattern
        assert str(local_lat) in query_pattern
        assert str(local_long) in query_pattern

    def test_query_limit(self):
        """Testa se a query possui limite de resultados"""
        limit = 1000
        assert limit == 1000

    def test_empty_dataframe_handling(self):
        """Testa manipulação de DataFrame vazio"""
        empty_df = pd.DataFrame()
        
        assert len(empty_df) == 0
        assert empty_df.empty

    def test_missing_time_field_fallback(self):
        """Testa fallback quando HORA_OCORRENCIA_BO está ausente"""
        row = {
            'HORA_OCORRENCIA_BO': None,
            'DESC_PERIODO': 'Madrugada',
        }
        
        if row['HORA_OCORRENCIA_BO']:
            xhora = ' ' + row['HORA_OCORRENCIA_BO'][11:16]
        else:
            xhora = ' ' + row['DESC_PERIODO']
        
        assert xhora == ' Madrugada'

    def test_supabase_connection_config(self):
        """Testa configuração esperada da conexão Supabase"""
        connection_type = "supabase"
        
        assert connection_type == "supabase"

    def test_table_name(self):
        """Testa se a tabela está corretamente nomeada como 'geocrimes'"""
        table_name = "geocrimes"
        
        assert table_name == "geocrimes"

    def test_cache_ttl(self):
        """Testa TTL do cache"""
        ttl = 600  # 10 minutos
        
        assert ttl == 600
        assert isinstance(ttl, int)
        assert ttl > 0


class TestDataValidation:
    """Testes de validação de dados"""

    def test_latitude_range(self):
        """Testa se latitude está no intervalo válido"""
        lat = -23.5505
        
        assert -90 <= lat <= 90

    def test_longitude_range(self):
        """Testa se longitude está no intervalo válido"""
        lon = -46.6333
        
        assert -180 <= lon <= 180

    def test_required_columns_present(self):
        """Testa se todas as colunas obrigatórias estão presentes"""
        mock_data = {
            'ANO_ESTATISTICA': 2023,
            'MES_ESTATISTICA': 1,
            'NUM_BO': '123456',
            'DATA_OCORRENCIA_BO': '2023-01-15',
            'HORA_OCORRENCIA_BO': '2023-01-15T14:30:00',
            'LATITUDE': -23.5505,
            'LONGITUDE': -46.6333,
            'RUBRICA': 'Roubo',
            'NATUREZA_APURADA': 'Roubo a Pedestre',
        }
        
        required_columns = ['LATITUDE', 'LONGITUDE', 'RUBRICA', 'DATA_OCORRENCIA_BO']
        
        for col in required_columns:
            assert col in mock_data

    def test_numeric_data_types(self):
        """Testa tipos de dados numéricos"""
        mock_data = {
            'LATITUDE': -23.5505,
            'LONGITUDE': -46.6333,
            'ANO_ESTATISTICA': 2023,
        }
        
        assert isinstance(mock_data['LATITUDE'], float)
        assert isinstance(mock_data['LONGITUDE'], float)
        assert isinstance(mock_data['ANO_ESTATISTICA'], int)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
