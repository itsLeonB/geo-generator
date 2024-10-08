import json
import psycopg2
import random


def get_db_data(keys):
    admin_areas = {}
    try:
        with psycopg2.connect('postgresql://postgres:postgres@localhost:5432/drugiz_db') as conn:
            print('Connected to Postgres')
            with conn.cursor() as cur:
                for key in keys:
                    cur.execute(
                        f"SELECT nama_kelurahan, kode_provinsi, kode_kabko, kode_kecamatan, kode_kelurahan, kode_pos FROM administrative_area WHERE nama_kabko ILIKE '%{key}%'")
                    print('Number of rows:', cur.rowcount)
                    admin_areas[key] = cur.fetchall()
                cur.execute("SELECT id, name FROM partners")

        return admin_areas
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def load():
    with open('data_points.json') as file:
        data = json.load(file)
        cities = data.keys()
        admin_areas = get_db_data(cities)
        print(admin_areas.keys())
        with open('pharmacies.sql', 'w') as sql_file:
            sql_file.write('\\SET ON_ERROR_STOP ON\n')
            sql_file.write('DROP TABLE IF EXISTS pharmacies CASCADE;\n')
            sql_file.write("""
            CREATE TABLE IF NOT EXISTS pharmacies (
                id BIGSERIAL PRIMARY KEY,
                partner_id INT NOT NULL REFERENCES partners (id),
                name VARCHAR(255) NOT NULL,
                address_detail VARCHAR(255) NOT NULL,
                province_id BIGINT NOT NULL REFERENCES administrative_area (kode_provinsi),
                city_id BIGINT NOT NULL REFERENCES administrative_area (kode_kabko),
                district_id BIGINT NOT NULL REFERENCES administrative_area (kode_kecamatan),
                village_id BIGINT NOT NULL REFERENCES administrative_area (kode_kelurahan),
                postal_code BIGINT NOT NULL REFERENCES administrative_area (kode_pos),
                long DECIMAL NOT NULL,
                lat DECIMAL NOT NULL,
                active BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                deleted_at TIMESTAMP
            );\n
            """)
            for city in cities:
                for coord in data[city]:
                    [long, lat] = coord
                    admin_area = random.choice(admin_areas[city])
                    sql_file.write(f"""
                    INSERT INTO pharmacies (partner_id, name, address_detail, province_id, city_id, district_id, village_id, postal_code, long, lat, active)
                    VALUES (partner_id, name, '{'Jalan ' + admin_area[0]}', {admin_area[1]}, {admin_area[2]}, {admin_area[3]}, {admin_area[4]}, {admin_area[5]}, {long}, {lat}, TRUE);
                    """)


if __name__ == '__main__':
    load()
