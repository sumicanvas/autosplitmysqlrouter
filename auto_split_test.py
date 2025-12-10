import mysql.connector
import sys

# ---------------------------------------------------------
# [mysql configuration]
# ---------------------------------------------------------
config = {
    'host': '127.0.0.1',       # Router IP
    'port': 6450,              # Auto Split Port
    'user': 'admin',            # MySQL account
    'password': 'Welcome#1',    # MySQL pwd
    'autocommit': True,        
    'use_pure': True
}

def prepare_database():
    print(">>> 0. Init: Check DB and Table...")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS testdb")
        cursor.execute("USE testdb")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS split_test (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                msg VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.close()
        conn.close()
        print("   ✅ DB Ready")
    except Exception as e:
        print(f"❌ Init Failed: {e}")
        sys.exit(1)

def get_server_info(conn):
    cursor = conn.cursor()
    # get hostname, port and so on
    cursor.execute("SELECT @@hostname, @@port, @@server_uuid, @@read_only")
    row = cursor.fetchone()
    cursor.close()
    
    return {
        'hostname': row[0], 
        'port': row[1], 
        'uuid': row[2], 
        'read_only': row[3]
    }

def run_test():
    prepare_database()
    
    target_str = f"{config['host']}:{config['port']}"
    print(f"\n🚀 [Target: {target_str}] Test Start\n")

    db_config = config.copy()
    db_config['database'] = 'testdb'

    # -----------------------------------------------------
    # 2. WRITE 테스트 (Primary 예상)
    # -----------------------------------------------------
    print(">>> 1. WRITE Transaction (Expect: Primary)")
    primary_uuid = None
    
    try:
        conn_write = mysql.connector.connect(**db_config)
        conn_write.start_transaction(readonly=False)
        
        info = get_server_info(conn_write)
        primary_uuid = info['uuid']
        
        # 포트 정보 출력
        print(f"   ✅ Server: {info['hostname']} (Port: {info['port']})")
        
        role = 'Secondary' if info['read_only'] else 'Primary'
        print(f"      Role  : {role}")
        
        cursor = conn_write.cursor()
        cursor.execute("INSERT INTO split_test (msg) VALUES ('RouterTest')")
        conn_write.commit()
        print("   📝 INSERT Success")
        conn_write.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Write Failed: {err}")
        sys.exit(1)

    # -----------------------------------------------------
    # 3. READ 테스트 (Secondary로 가야 함)
    # -----------------------------------------------------
    print("\n" + "="*30 + "\n")
    print(">>> 2. READ Transaction (Expect: Secondary)")
    secondary_uuid = None
    
    try:
        conn_read = mysql.connector.connect(**db_config)
        conn_read.start_transaction(readonly=True)
        
        info = get_server_info(conn_read)
        secondary_uuid = info['uuid']
        
        # 포트 정보 출력
        print(f"   ✅ Server: {info['hostname']} (Port: {info['port']})")
        
        role = 'Secondary' if info['read_only'] else 'Primary'
        print(f"      Role  : {role}")
        
        cursor = conn_read.cursor()
        cursor.execute("SELECT count(*) FROM split_test")
        cnt = cursor.fetchone()[0]
        print(f"   📖 SELECT Success (Count: {cnt})")
        
        conn_read.commit()
        conn_read.close()

    except mysql.connector.Error as err:
        print(f"❌ Read Failed: {err}")

    # -----------------------------------------------------
    # 4. 결과 출력
    # -----------------------------------------------------
    print("\n" + "-"*30)
    print("📊 [Final Result]")
    
    if primary_uuid != secondary_uuid:
        print("🎉 SUCCESS!")
        print("   Write -> Primary")
        print("   Read  -> Secondary")
        print("   (Different Servers Used)")
    else:
        print("ℹ️ Check Required")
        print("   Write & Read processed on the SAME server.")

if __name__ == "__main__":
    run_test()