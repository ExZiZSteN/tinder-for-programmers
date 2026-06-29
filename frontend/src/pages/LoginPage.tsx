import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/authStore'
import { loginSchema, type LoginFormData } from '@/lib/validations'

export default function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData, e?: React.BaseSyntheticEvent) => {
    e?.preventDefault() // Явно предотвращаем reload формы
  
    try {
      // 1. Логинимся
      const { access_token, refresh_token } = await authApi.login({
        email: data.email,
        password: data.password,
      })

      setAuth(
        {
          id: 0,
          email: data.email,
          full_name: '',
          skills: [],
          user_role: 'user',
          is_active: true,
          created_at: '',
        },
        access_token,
        refresh_token
      )
      // 2. Получаем данные пользователя
      const user = await authApi.getMe()
      // 3. Сохраняем в store
      setAuth(user, access_token, refresh_token)

      toast.success('Добро пожаловать!')
      navigate('/feed', { replace: true })
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Ошибка входа'
      toast.error(message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Tinder for Developers
            </h1>
            <p className="text-gray-600">
              Войдите в свой аккаунт
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email */}
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                error={errors.email?.message}
                {...register('email')}
              />
            </div>

            {/* Password */}
            <div>
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                autoComplete="current-password"
                error={errors.password?.message}
                {...register('password')}
              />
            </div>

            {/* Submit */}
            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={isSubmitting}
            >
              Войти
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Нет аккаунта?{' '}
              <Link
                to="/register"
                className="font-medium text-primary hover:text-primary/80"
              >
                Зарегистрироваться
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}