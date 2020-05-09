from app.npi.npi_manager import NpiManager





if __name__ == '__main__':
    npi = NpiManager('COM3')

    while(1):
        npi_msg = npi.process_next_msg()
        print(npi_msg)
