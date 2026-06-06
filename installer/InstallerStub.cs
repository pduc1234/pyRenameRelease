using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;
using System.IO.Compression;
using Microsoft.Win32;

namespace FileRenamerInstaller
{
    internal static class Program
    {
        private const string AppName = "FileRenamer";
        private const string UninstallerName = "Uninstall FileRenamer.exe";
        private const string UninstallRegistryPath = @"Software\Microsoft\Windows\CurrentVersion\Uninstall\FileRenamer";
        private static readonly byte[] PayloadMarker = Encoding.ASCII.GetBytes("\n--FILERENAMER-PAYLOAD-V1--\n");

        [STAThread]
        private static int Main(string[] args)
        {
            if (IsUninstallMode(args))
            {
                return Uninstall(args);
            }

            return Install();
        }

        private static bool IsUninstallMode(string[] args)
        {
            foreach (string arg in args)
            {
                if (string.Equals(arg, "--uninstall", StringComparison.OrdinalIgnoreCase))
                {
                    return true;
                }
            }

            string fileName = Path.GetFileName(Assembly.GetExecutingAssembly().Location);
            return string.Equals(fileName, UninstallerName, StringComparison.OrdinalIgnoreCase);
        }

        private static int Install()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), AppName + "_Install_" + Guid.NewGuid().ToString("N"));

            try
            {
                Directory.CreateDirectory(tempRoot);

                string payloadZip = Path.Combine(tempRoot, AppName + ".zip");
                ExtractPayload(Assembly.GetExecutingAssembly().Location, payloadZip);

                ZipFile.ExtractToDirectory(payloadZip, tempRoot);

                string payloadRoot = Path.Combine(tempRoot, AppName);
                string payloadExe = Path.Combine(payloadRoot, AppName + ".exe");
                if (!File.Exists(payloadExe))
                {
                    throw new InvalidOperationException("Invalid installer payload.");
                }

                string installRoot = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "Programs",
                    AppName);

                if (Directory.Exists(installRoot))
                {
                    Directory.Delete(installRoot, true);
                }

                CopyDirectory(payloadRoot, installRoot);
                CreateShortcuts(installRoot);
                CreateUninstaller(installRoot);
                CreateUninstallRegistryEntry(installRoot);

                MessageBox.Show(
                    AppName + " installed successfully.\n\nLocation: " + installRoot,
                    AppName + " Installer",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);

                return 0;
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    "Installation failed:\n\n" + ex.Message,
                    AppName + " Installer",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);

                return 1;
            }
            finally
            {
                TryDeleteDirectory(tempRoot);
            }
        }

        private static int Uninstall(string[] args)
        {
            bool quiet = HasArgument(args, "--quiet");
            string installRoot = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Programs",
                AppName);

            try
            {
                if (!quiet)
                {
                    DialogResult answer = MessageBox.Show(
                        "Uninstall " + AppName + "?",
                        AppName + " Uninstaller",
                        MessageBoxButtons.YesNo,
                        MessageBoxIcon.Question);

                    if (answer != DialogResult.Yes)
                    {
                        return 0;
                    }
                }

                DeleteShortcuts();
                DeleteUninstallRegistryEntry();
                ScheduleInstallDirectoryDeletion(installRoot);

                if (!quiet)
                {
                    MessageBox.Show(
                        AppName + " was uninstalled.",
                        AppName + " Uninstaller",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                }

                return 0;
            }
            catch (Exception ex)
            {
                if (!quiet)
                {
                    MessageBox.Show(
                        "Uninstall failed:\n\n" + ex.Message,
                        AppName + " Uninstaller",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
                }

                return 1;
            }
        }

        private static bool HasArgument(string[] args, string expected)
        {
            foreach (string arg in args)
            {
                if (string.Equals(arg, expected, StringComparison.OrdinalIgnoreCase))
                {
                    return true;
                }
            }

            return false;
        }

        private static void ExtractPayload(string installerPath, string payloadZip)
        {
            byte[] bytes = File.ReadAllBytes(installerPath);
            int markerIndex = LastIndexOf(bytes, PayloadMarker);
            if (markerIndex < 0)
            {
                throw new InvalidOperationException("Installer payload marker was not found.");
            }

            int payloadStart = markerIndex + PayloadMarker.Length;
            using (FileStream output = File.Create(payloadZip))
            {
                output.Write(bytes, payloadStart, bytes.Length - payloadStart);
            }
        }

        private static int LastIndexOf(byte[] source, byte[] pattern)
        {
            for (int i = source.Length - pattern.Length; i >= 0; i--)
            {
                bool matched = true;
                for (int j = 0; j < pattern.Length; j++)
                {
                    if (source[i + j] != pattern[j])
                    {
                        matched = false;
                        break;
                    }
                }

                if (matched)
                {
                    return i;
                }
            }

            return -1;
        }

        private static void CopyDirectory(string sourceDir, string destinationDir)
        {
            Directory.CreateDirectory(destinationDir);

            foreach (string directory in Directory.GetDirectories(sourceDir, "*", SearchOption.AllDirectories))
            {
                Directory.CreateDirectory(directory.Replace(sourceDir, destinationDir));
            }

            foreach (string file in Directory.GetFiles(sourceDir, "*", SearchOption.AllDirectories))
            {
                string target = file.Replace(sourceDir, destinationDir);
                File.Copy(file, target, true);
            }
        }

        private static void CreateShortcuts(string installRoot)
        {
            string exePath = Path.Combine(installRoot, AppName + ".exe");
            string startMenuDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs",
                AppName);
            string desktopShortcut = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),
                AppName + ".lnk");

            Directory.CreateDirectory(startMenuDir);
            CreateShortcut(Path.Combine(startMenuDir, AppName + ".lnk"), exePath, installRoot);
            CreateShortcut(desktopShortcut, exePath, installRoot);
        }

        private static void CreateUninstaller(string installRoot)
        {
            string source = Assembly.GetExecutingAssembly().Location;
            string destination = Path.Combine(installRoot, UninstallerName);
            File.Copy(source, destination, true);
        }

        private static void CreateUninstallRegistryEntry(string installRoot)
        {
            string appExe = Path.Combine(installRoot, AppName + ".exe");
            string uninstaller = Path.Combine(installRoot, UninstallerName);

            using (RegistryKey key = Registry.CurrentUser.CreateSubKey(UninstallRegistryPath))
            {
                if (key == null)
                {
                    throw new InvalidOperationException("Could not create uninstall registry entry.");
                }

                key.SetValue("DisplayName", AppName, RegistryValueKind.String);
                key.SetValue("DisplayIcon", appExe, RegistryValueKind.String);
                key.SetValue("InstallLocation", installRoot, RegistryValueKind.String);
                key.SetValue("Publisher", "FileRenamer", RegistryValueKind.String);
                key.SetValue("UninstallString", Quote(uninstaller), RegistryValueKind.String);
                key.SetValue("QuietUninstallString", Quote(uninstaller) + " --quiet", RegistryValueKind.String);
                key.SetValue("NoModify", 1, RegistryValueKind.DWord);
                key.SetValue("NoRepair", 1, RegistryValueKind.DWord);
                key.SetValue("EstimatedSize", EstimateDirectorySizeKb(installRoot), RegistryValueKind.DWord);
            }
        }

        private static int EstimateDirectorySizeKb(string directory)
        {
            long totalBytes = 0;
            foreach (string file in Directory.GetFiles(directory, "*", SearchOption.AllDirectories))
            {
                totalBytes += new FileInfo(file).Length;
            }

            long totalKb = Math.Max(1, totalBytes / 1024);
            return totalKb > int.MaxValue ? int.MaxValue : (int)totalKb;
        }

        private static string Quote(string value)
        {
            return "\"" + value + "\"";
        }

        private static void DeleteShortcuts()
        {
            string startMenuDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs",
                AppName);
            string desktopShortcut = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),
                AppName + ".lnk");

            if (File.Exists(desktopShortcut))
            {
                File.Delete(desktopShortcut);
            }

            if (Directory.Exists(startMenuDir))
            {
                Directory.Delete(startMenuDir, true);
            }
        }

        private static void DeleteUninstallRegistryEntry()
        {
            Registry.CurrentUser.DeleteSubKeyTree(UninstallRegistryPath, false);
        }

        private static void ScheduleInstallDirectoryDeletion(string installRoot)
        {
            if (!Directory.Exists(installRoot))
            {
                return;
            }

            string command = "/C timeout /t 2 /nobreak > nul & rmdir /s /q " + Quote(installRoot);
            ProcessStartInfo startInfo = new ProcessStartInfo("cmd.exe", command);
            startInfo.CreateNoWindow = true;
            startInfo.WindowStyle = ProcessWindowStyle.Hidden;
            Process.Start(startInfo);
        }

        private static void CreateShortcut(string shortcutPath, string targetPath, string workingDirectory)
        {
            Type shellType = Type.GetTypeFromProgID("WScript.Shell");
            if (shellType == null)
            {
                return;
            }

            object shell = Activator.CreateInstance(shellType);
            try
            {
                object shortcut = shellType.InvokeMember(
                    "CreateShortcut",
                    BindingFlags.InvokeMethod,
                    null,
                    shell,
                    new object[] { shortcutPath });

                Type shortcutType = shortcut.GetType();
                shortcutType.InvokeMember("TargetPath", BindingFlags.SetProperty, null, shortcut, new object[] { targetPath });
                shortcutType.InvokeMember("WorkingDirectory", BindingFlags.SetProperty, null, shortcut, new object[] { workingDirectory });
                shortcutType.InvokeMember("IconLocation", BindingFlags.SetProperty, null, shortcut, new object[] { targetPath });
                shortcutType.InvokeMember("Save", BindingFlags.InvokeMethod, null, shortcut, null);
            }
            finally
            {
                Marshal.FinalReleaseComObject(shell);
            }
        }

        private static void TryDeleteDirectory(string path)
        {
            try
            {
                if (Directory.Exists(path))
                {
                    Directory.Delete(path, true);
                }
            }
            catch
            {
            }
        }
    }
}
