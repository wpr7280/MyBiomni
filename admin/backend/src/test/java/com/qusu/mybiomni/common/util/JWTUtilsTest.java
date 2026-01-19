package com.qusu.mybiomni.common.util;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.Test;

import javax.crypto.SecretKey;
import java.util.Date;

public class JWTUtilsTest {
    private static String secret ="mySecretKeyForJWTWhichShouldBeLongEnoughForHS512AlgorithmAndSecurityPurposes" ;
    //365天有效期
    private static long expiration = 86400000 * 365;
    public static String generateToken(String userId, String email) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);

        return Jwts.builder()
                .subject(userId)
                .claim("email", email)
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }
    private static SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(secret.getBytes());
    }
    @Test
    public void testGenerateToken() {
        String token = generateToken("e926e5dd-879e-498c-862e-aa9e2bfebac8", "e2b@example.com");
        System.out.println(token);
    }
}
