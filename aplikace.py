import psycopg

# =========================
# 🔌 Připojení
# =========================
def connect():
    return psycopg.connect(
        host="192.168.135.10",
        port=5432,
        dbname="obce",
        user="student",
        password="bluemonkey3"
    )


# =========================
# 🗄️ DATOVÁ VRSTVA
# =========================
def get_okresy(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id_okres, nazev FROM okresy ORDER BY id_okres")
        return cur.fetchall()


def get_obce_v_okrese(conn, kod):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT nazev, pocet_obyvatel, prumerny_vek
            FROM obce_pob
            WHERE id_okres = %s
            ORDER BY pocet_obyvatel DESC
        """, (kod,))
        return cur.fetchall()


def get_hledani(conn, text):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT nazev
            FROM obce_pob
            WHERE nazev ILIKE %s
        """, (f"%{text}%",))
        return cur.fetchall()


def get_statistika(conn, kod):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                SUM(pocet_obyvatel),
                AVG(prumerny_vek),
                SUM(pocet_muzi),
                SUM(pocet_zeny)
            FROM obce_pob
            WHERE id_okres = %s
        """, (kod,))
        return cur.fetchone()


# =========================
# 🖥️ UI (konzole)
# =========================
def menu():
    print("\n--- DEMOGRAFIE ČR ---")
    print("1 - Okresy")
    print("2 - Obce v okrese")
    print("3 - Hledat obec")
    print("4 - Statistiky")
    print("0 - Konec")


# =========================
# ▶️ MAIN
# =========================
def main():
    conn = connect()

    while True:
        menu()
        volba = input("Vyber: ")

        if volba == "1":
            for row in get_okresy(conn):
                print(row[0], row[1])

        elif volba == "2":
            kod = input("Kód okresu: ")
            data = get_obce_v_okrese(conn, kod)

            if data:
                for row in data:
                    print(f"{row[0]} | {row[1]} | {round(row[2],1)}")
            else:
                print("Žádná data")

        elif volba == "3":
            text = input("Název: ")
            data = get_hledani(conn, text)

            if data:
                for row in data:
                    print(row[0])
            else:
                print("Nic nenalezeno")

        elif volba == "4":
            kod = input("Kód okresu: ")
            row = get_statistika(conn, kod)

            if row and row[0]:
                print("Obyvatel:", row[0])
                print("Průměrný věk:", round(row[1], 2))
                print("Muži:", row[2])
                print("Ženy:", row[3])
            else:
                print("Žádná data")

        elif volba == "0":
            break

        else:
            print("Špatná volba")

    conn.close()


if __name__ == "__main__":
    main()