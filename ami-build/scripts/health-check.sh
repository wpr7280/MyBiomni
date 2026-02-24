#!/bin/bash
# Biomni Health Check Script

echo "╔══════════════════════════════════════╗"
echo "║     Biomni Health Check Report       ║"
echo "╚══════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

check() {
    local name=$1
    local result=$2
    if [ "$result" = "0" ]; then
        echo "  ✅ $name"
        ((PASS++))
    else
        echo "  ❌ $name"
        ((FAIL++))
    fi
}

echo "── Docker Containers ──"
docker inspect -f '{{.State.Running}}' mysql57 2>/dev/null | grep -q true; check "MySQL (docker)" $?
docker inspect -f '{{.State.Running}}' redis72 2>/dev/null | grep -q true; check "Redis (docker)" $?

echo ""
echo "── Services ──"
systemctl is-active --quiet biomni-admin;   check "Admin Backend" $?
systemctl is-active --quiet biomni-agent;   check "Agent" $?
systemctl is-active --quiet nginx;          check "Nginx" $?

echo ""
echo "── Ports ──"
ss -tlnp | grep -q ':3306 ';  check "MySQL (3306)" $?
ss -tlnp | grep -q ':6379 ';  check "Redis (6379)" $?
ss -tlnp | grep -q ':9999 ';  check "Admin Backend (9999)" $?
ss -tlnp | grep -q ':8000 ';  check "Agent (8000)" $?
ss -tlnp | grep -q ':80 ';    check "Nginx (80)" $?

echo ""
echo "── HTTP Endpoints ──"
curl -sf http://127.0.0.1:9999/health/alive > /dev/null 2>&1; check "Admin /health/alive" $?
curl -sf http://127.0.0.1:8000/health > /dev/null 2>&1;       check "Agent /health" $?
curl -sf http://127.0.0.1/ > /dev/null 2>&1;                  check "Client Frontend" $?
curl -sf http://127.0.0.1/admin/ > /dev/null 2>&1;            check "Admin Frontend" $?

echo ""
echo "── Resources ──"
DISK_USAGE=$(df / --output=pcent | tail -1 | tr -d ' %')
MEM_USAGE=$(free | awk '/Mem:/{printf "%.0f", $3/$2*100}')
echo "  Disk: ${DISK_USAGE}% used"
echo "  Memory: ${MEM_USAGE}% used"
[ "$DISK_USAGE" -lt 85 ]; check "Disk < 85%" $?
[ "$MEM_USAGE" -lt 90 ];  check "Memory < 90%" $?

echo ""
echo "══════════════════════════════════════"
echo "  Result: ${PASS} passed, ${FAIL} failed"
echo "══════════════════════════════════════"

exit $FAIL
