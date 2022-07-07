import happybase

def create_table(conn, table, families):
    """
    :return: 创建表
    """
    print('Creating table <{}>........'.format(table))
    if bytes(table, 'ascii') in conn.tables():
        print('<{}> already exists.'.format(table))
    else:
        try:
            conn.create_table(table, families)
            print('Successful to create table <{}>'.format(table))
        except:
            print('Failed to create table <{}>'.format(table))


con = happybase.Connection('172.31.41.139',9090, autoconnect=False)

con.open()  # 打开thrift传输'TCP连接

families = {
        'cf1': dict(max_versions=1),
    }
create_table(con, 'hbase_client_info_1', families)
create_table(con, 'hbase_client_info_2', families)
create_table(con, 'hbase_client_info_3', families)
create_table(con, 'hbase_client_info_4', families)
create_table(con, 'hbase_client_info_5', families)