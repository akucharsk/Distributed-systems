package zad4;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Arrays;


public class JavaUDPClient4 {
    public static void main(String[] args) {
        DatagramSocket socket = null;
        final String host = "localhost";
        final int port = Integer.parseInt(args[0]);

        final int serverPort = args.length > 1 ? Integer.parseInt(args[1]) : 8008;
        final String serverAddr = args.length > 2 ? args[2] : host;

        try {
            socket = new DatagramSocket(port, InetAddress.getByName(host));
            BufferedReader in = new BufferedReader(new InputStreamReader(System.in), 1023);
            byte[] buffer = new byte[1024];
            while (true) {
                Arrays.fill(buffer, (byte) 0);
                String msg = in.readLine();
                msg = "J" + msg;
                DatagramPacket packet = new DatagramPacket(msg.getBytes(), msg.getBytes().length,
                        InetAddress.getByName(serverAddr), serverPort);
                socket.send(packet);
                System.out.println("---Message sent---");
                DatagramPacket received = new DatagramPacket(buffer, buffer.length);
                socket.receive(received);
                System.out.printf("Received from server:\n %s\n\n", new String(received.getData()));
            }

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (socket != null) {
                socket.close();
            }
        }
    }
}
