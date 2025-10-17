# Test RLS policies
Write-Host "Testing RLS policies..."

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/setup/test-rls" -Method GET
    Write-Host "Success: $($response.success)"
    Write-Host "All tables accessible: $($response.all_tables_accessible)"
    Write-Host "Note: $($response.note)"
    Write-Host ""
    Write-Host "Table Test Results:"
    foreach ($test in $response.rls_test_results) {
        Write-Host "- $($test.table): accessible=$($test.accessible), count=$($test.count)"
        if ($test.error) {
            Write-Host "  Error: $($test.error)"
        }
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
